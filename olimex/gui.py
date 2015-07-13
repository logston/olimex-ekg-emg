"""
This module defines logic for plotting exg data in real-time.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import scipy.ndimage
import serial

from olimex.constants import DEFAULT_BAUDRATE
from olimex.exg import PacketStreamReader
from olimex.mock import FakeSerialByteArray


STRIP_LENGTH_SECONDS = 6
DOTS_PER_SECOND = 250
DOTS_PER_02_SECOND = DOTS_PER_SECOND / 5
DOTS_PER_004_SECOND = DOTS_PER_SECOND / 25
DOTS_PER_STRIP_LENGTH = DOTS_PER_SECOND * STRIP_LENGTH_SECONDS
DOTS_PER_STRIP_HEIGHT = 1025
DOTS_MAX_GRAPH_HEIGHT = 1023

REFRESHES_PER_SECOND = 25
REFRESH_INTERVAL_MS = 1000 / REFRESHES_PER_SECOND
DOTS_TO_JUMP_PER_REFRESH = DOTS_PER_SECOND / REFRESHES_PER_SECOND

mpl.rcParams['savefig.dpi'] = 600
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['lines.linewidth'] = 0.35

fig, axes = plt.subplots(figsize=(STRIP_LENGTH_SECONDS, STRIP_LENGTH_SECONDS / 3),
                         dpi=DOTS_PER_SECOND)

axes.set_ylim(0, DOTS_PER_STRIP_HEIGHT)
axes.set_xlim(0, DOTS_PER_STRIP_LENGTH)
axes.xaxis.set_visible(False)
axes.yaxis.set_visible(False)


def get_new_data_points(packet_reader):
    """
    Return all data points in the buffer waiting to be displayed.

    In between refreshes of the graph, data points will be
    read into a waiting buffer where they are held before
    they are displayed during the next refresh. The packet
    reader is responsible for managing that buffer.
    """
    SAMPLES_PER_004_SECOND = int(5)
    while True:
        new_data = np.array([DOTS_PER_STRIP_HEIGHT / 2
                             for _ in range(SAMPLES_PER_004_SECOND)])
        for i, _ in enumerate(range(SAMPLES_PER_004_SECOND)):
            channel_values = next(packet_reader)
            if channel_values:
                channel_1, *_ = channel_values
                new_data[i] = channel_1
        new_data = scipy.ndimage.zoom(new_data, 1, order=0)
        yield new_data


def axes_updater(axes, packet_reader):
    """
    Update exg figure.

    This function will update the exg figure.

    :param axes:
    :param packet_reader:
    """
    minor_grid_points = np.arange(0, DOTS_PER_STRIP_LENGTH, DOTS_PER_004_SECOND)
    axes.vlines(minor_grid_points, 0, DOTS_PER_STRIP_HEIGHT, color='r', alpha=0.3)
    major_grid_points = np.arange(0,DOTS_PER_STRIP_LENGTH, DOTS_PER_02_SECOND)
    axes.vlines(major_grid_points, 0, DOTS_PER_STRIP_HEIGHT, color='r', alpha=0.9)

    # Start the graph off with a flat vertically-centered line
    ydata = np.array([DOTS_PER_STRIP_HEIGHT / 2
                      for _ in range(DOTS_PER_STRIP_LENGTH)])
    line, = axes.plot(range(DOTS_PER_STRIP_LENGTH), ydata)

    new_data_gen = get_new_data_points(packet_reader)
    while True:
        new_data = next(new_data_gen)

        # Remove old data points, add new ones
        ydata = np.delete(ydata, range(len(new_data)))
        ydata = np.append(ydata, new_data)
        line.set_ydata(ydata)
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

    axes_updater_gen = axes_updater(axes, reader)
    animation.FuncAnimation(fig, lambda _: next(axes_updater_gen),
                            interval=REFRESH_INTERVAL_MS)
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
