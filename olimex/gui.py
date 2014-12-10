"""
This module defines logic for plotting exg data in real-time.
"""
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial
from olimex.constants import DEFAULT_BAUDRATE

from olimex.exg import PacketStreamReader
from olimex.mock import SerialMocked
from olimex.utils import calculate_heart_rate


def update_generator(axes, reader, from_file=False):
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

    while True:
        new_samples = []
        if from_file:
            packets_in_waiting = 1
            values = next(reader)
            if values:
                (channel_1, _, _, _, _, _) = values
                # Transform graph, stretch the x axis
                for _ in range(period_multiplier):
                    new_samples.append(channel_1)
        else:
            packets_in_waiting = reader.packets_in_waiting
            while len(new_samples) / period_multiplier < packets_in_waiting:
                values = next(reader)
                if values:
                    (channel_1, _, _, _, _, _) = values
                    # Transform graph, stretch the x axis
                    for _ in range(period_multiplier):
                        new_samples.append(channel_1)

        data = np.concatenate((data[packets_in_waiting * period_multiplier:],
                               np.array(new_samples)))
        # Add new data to plot
        line.set_ydata(data)

        # TODO
        # Calculate heart rate
        # heart_rate = calculate_heart_rate(data)
        # ax.text(0.98, 0.95, '{} HR'.format(heart_rate),
        #         fontsize=15, transform=ax.transAxes, horizontalalignment='right')

        # Calibrate y axis limits
        amax = np.amax(data)
        amin = np.amin(data)
        total_amplitude = amax - amin
        margin = total_amplitude * 0.1
        axes.set_ylim(amin - margin, amax + margin)
        yield


def show_exg_for_port(port):
    """
    Create and display a real-time :ref:`exg <exg>` figure.

    This function will create a new matplotlib figure and make
    a call to :py:class:`~matplotlib.animation.FuncAnimation` to
    begin plotting the :ref:`exg <exg>`.

    :param port: Serial port being sent exg packets.
    :type port: str
    """
    fig, axes = plt.subplots()
    # instantiate a packet reader
    serial_obj = serial.Serial(port, DEFAULT_BAUDRATE)
    reader = PacketStreamReader(serial_obj)
    update_gen = update_generator(axes, reader)
    animation.FuncAnimation(fig, lambda _: next(update_gen), interval=50)
    plt.show()


def show_exg_for_file(file):
    """
    Create and display an :ref:`exg <exg>` figure.

    This function will create a new matplotlib figure and make
    a call to :py:class:`~matplotlib.animation.FuncAnimation` to
    begin plotting the :ref:`exg <exg>`.

    :param file: File to stream EXG data from.
    :type file: str
    """
    fig, axes = plt.subplots()
    # instantiate a packet reader
    with SerialMocked(file) as serial_obj:
        reader = PacketStreamReader(serial_obj)
        update_gen = update_generator(axes, reader, from_file=True)
        animation.FuncAnimation(fig, lambda _: next(update_gen), interval=8)
        plt.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run GUI for Olimex-EKG-EMG.')
    parser.add_argument('-p', '--port',
                        dest='port',
                        help='Port to which an Arduino is connected (eg. /dev/tty.usbmodem1411)')
    parser.add_argument('-f', '--file',
                        dest='file',
                        help='File to stream EXG data from.')
    args = parser.parse_args()

    if args.port:
        show_exg_for_port(args.port)
    elif args.file:
        show_exg_for_file(args.file)
    else:
        parser.print_help()

