"""
This module defines logic for plotting exg data in real-time.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
from olimex.constants import DEFAULT_BAUDRATE

from olimex.exg import PacketStreamReader
from olimex.mock import FakeSerialByteArray
from olimex.utils import calculate_heart_rate


def axes_refresher_generator(axes, reader):
    """
    Update exg figure.

    This function will update the exg figure.

    :param axes:
    :param reader:
    """
    samples_per_graph = 2560
    period_multiplier = 2

    axes.set_ylim(0, 1024)
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)

    # initialize plot with zeros
    data = np.zeros(samples_per_graph)
    line, = axes.plot(data)

    # A counter to keep track of how many times the
    # axes on the figure has been refreshed.
    refresh_counter = 0

    while True:
        new_packets = []
        # Calculate the number of new packets that need to be
        # read during this refresh.
        packet_grab_count = 6 if refresh_counter % 4 else 7
        refresh_counter += 1
        for _ in range(packet_grab_count):
            channel_values = next(reader)
            if channel_values:
                channel_1, *_ = channel_values
                # Transform graph, stretch the x axis
                for _ in range(period_multiplier):
                    new_packets.append(channel_1)

        data = np.concatenate((data[len(new_packets):], np.array(new_packets)))

        # Add new data to plot
        line.set_ydata(data)

        # TODO
        # Calculate heart rate
        heart_rate = calculate_heart_rate(data)
        print(heart_rate)
        # ax.text(0.98, 0.95, '{} HR'.format(heart_rate),
        #         fontsize=15, transform=ax.transAxes, horizontalalignment='right')

        # Calibrate y axis limits
        amax = np.amax(data)
        amin = np.amin(data)
        if amin != amax:
            total_amplitude = amax - amin
            margin = total_amplitude * 0.1
            axes.set_ylim(amin - margin, amax + margin)
        yield


def show_exg(source, source_type='port'):
    """
    Create and display a real-time :ref:`exg <exg>` figure.

    This function will create a new matplotlib figure and make
    a call to :py:class:`~matplotlib.animation.FuncAnimation` to
    begin plotting the :ref:`exg <exg>`.

    :param source: Serial port being sent exg packets or
                   file path to file containing saved exg data.
    :type source: str
    """
    # instantiate a packet reader
    if source_type == 'file':
        with open(source, 'rb') as fd:
            buff = bytearray(fd.read())
        serial_obj = FakeSerialByteArray(buff)
    else:
        serial_obj = serial.Serial(source, DEFAULT_BAUDRATE)

    reader = PacketStreamReader(serial_obj)

    fig, axes = plt.subplots()
    axes_refresher = axes_refresher_generator(axes, reader)
    animation.FuncAnimation(fig, lambda _: next(axes_refresher), interval=50)
    plt.show()


def run_gui():
    import argparse

    parser = argparse.ArgumentParser(description='Run GUI for Olimex-EKG-EMG.')
    parser.add_argument('-p', '--port',
                        dest='port',
                        help='Port to which an Arduino is connected (eg. /dev/tty.usbmodem1411)')
    parser.add_argument('-f', '--file',
                        dest='file',
                        help='File to stream EXG data from. Loads entire file prior to display.')
    args = parser.parse_args()

    if args.port:
        show_exg(args.port)
    elif args.file:
        show_exg(args.file, source_type='file')
    else:
        parser.print_help()


if __name__ == '__main__':
    run_gui()
