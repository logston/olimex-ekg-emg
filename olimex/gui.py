"""
This module defines logic for plotting exg data in real-time.
"""
import argparse
import os
import sys

try:
    import tkinter
except ImportError:
    print('exg requires tkinter to be installed')
    sys.exit(1)

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import scipy.ndimage
import serial

from olimex.constants import DEFAULT_BAUDRATE, SAMPLE_FREQUENCY
from olimex.exg import PacketStreamReader
from olimex.mock import FakeSerialByteArray
from olimex.utils import calculate_heart_rate, get_mock_data_list

# Packets are coming in at 125 packets per second
# Ie. Every 8 ms, a packet is received
# This plot refreshes every 40 ms to achieve 25fps
# Thus every refresh, 5 new packets should be added to the
# strip (40 ms / 8 ms = 5).
# Each dot should take up 4 ms (1000 ms / 250 dots).
# Each packet should be 2 dots. 
# (1 dot / 4 ms) * (8 ms / packet) = 2 dots / packet
# The strip should move 10 dots per refresh 
# (2 dots / packet) * (5 packets / refresh) = 10 dots / refresh

STRIP_LENGTH_SECONDS = 6
DOTS_PER_SECOND = 250
DOTS_PER_02_SECOND = DOTS_PER_SECOND / 5
DOTS_PER_004_SECOND = DOTS_PER_SECOND / 25
DOTS_PER_STRIP_LENGTH = DOTS_PER_SECOND * STRIP_LENGTH_SECONDS
DOTS_PER_STRIP_HEIGHT = 1025
DOTS_MAX_GRAPH_HEIGHT = 1023

SAMPLES_PER_004_SECOND = int(5)

REFRESHES_PER_SECOND = 25
REFRESH_INTERVAL_MS = 1000 / REFRESHES_PER_SECOND
DOTS_TO_JUMP_PER_REFRESH = DOTS_PER_SECOND / REFRESHES_PER_SECOND

mpl.rcParams['savefig.dpi'] = 600
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['lines.linewidth'] = 0.35


INITIAL_VOLTAGE = DOTS_PER_STRIP_HEIGHT / 2


def get_new_data_points(packet_reader):
    """
    Return all data points in the buffer waiting to be displayed.

    In between refreshes of the graph, data points will be
    read into a waiting buffer where they are held before
    they are displayed during the next refresh. The packet
    reader is responsible for managing that buffer.
    """
    range_samples_per_004_second = range(SAMPLES_PER_004_SECOND)
    while True:
        new_data = np.array([INITIAL_VOLTAGE for _ in range_samples_per_004_second])
        for i, _ in enumerate(range_samples_per_004_second):
            channel_values = next(packet_reader)
            if channel_values:
                channel_1, *_ = channel_values
                new_data[i] = channel_1
        new_data = scipy.ndimage.zoom(new_data, DOTS_PER_SECOND / SAMPLE_FREQUENCY,
                                      order=0)
        yield new_data


def axes_updater(axes, packet_reader):
    """
    Update exg figure.

    This function will update the exg figure.

    :param axes:
    :param packet_reader:
    """
    minor_vgrid_points = np.arange(0, DOTS_PER_STRIP_LENGTH, DOTS_PER_004_SECOND)
    axes.vlines(minor_vgrid_points, 0, DOTS_PER_STRIP_HEIGHT, color='r', alpha=0.3)

    minor_hgrid_points = np.arange(0, DOTS_PER_STRIP_HEIGHT, 1.75 * DOTS_PER_004_SECOND)
    axes.hlines(minor_hgrid_points, 0, DOTS_PER_STRIP_LENGTH, color='r', alpha=0.3)

    major_vgrid_points = np.arange(0, DOTS_PER_STRIP_LENGTH, DOTS_PER_02_SECOND)
    axes.vlines(major_vgrid_points, 0, DOTS_PER_STRIP_HEIGHT, color='r', alpha=0.9)

    major_hgrid_points = np.arange(0, DOTS_PER_STRIP_HEIGHT, 1.75 * DOTS_PER_02_SECOND)
    axes.hlines(major_hgrid_points, 0, DOTS_PER_STRIP_LENGTH, color='r', alpha=0.9)

    # Start the graph off with a flat vertically-centered line
    ydata = np.array([INITIAL_VOLTAGE for _ in range(DOTS_PER_STRIP_LENGTH)])
    line, = axes.plot(range(DOTS_PER_STRIP_LENGTH), ydata)

    new_data_gen = get_new_data_points(packet_reader)
    delete_indicies= range(int(SAMPLES_PER_004_SECOND * (DOTS_PER_SECOND / SAMPLE_FREQUENCY)))
    while True:
        new_data = next(new_data_gen)

        # Remove old data points, add new ones
        ydata = np.delete(ydata, delete_indicies)
        ydata = np.append(ydata, new_data)
        line.set_ydata(ydata)
        yield


def show_exg(source, source_type='port', print_timing_data=False):
    """
    Create and display a real-time :ref:`exg <exg>` figure.

    This function will create a new matplotlib figure and make
    a call to :py:class:`~matplotlib.animation.FuncAnimation` to
    begin plotting the :ref:`exg <exg>`.

    :param source: Serial port being sent exg packets or
                   file path to file containing saved exg data.
    :type source: str
    """
    if source_type == 'file':
        print('Loading data...', end='', flush=True)
        with open(source, 'rb') as fd:
            buff = bytearray(fd.read())
        serial_obj = FakeSerialByteArray(buff)
        print('Done.')

    else:
        serial_obj = serial.Serial(source, DEFAULT_BAUDRATE)

    reader = PacketStreamReader(serial_obj)

    fig, axes = plt.subplots(figsize=(STRIP_LENGTH_SECONDS,
                                      STRIP_LENGTH_SECONDS / 3),
                             dpi=DOTS_PER_SECOND)
    fig.canvas.set_window_title(source)
    axes.set_ylim(0, DOTS_PER_STRIP_HEIGHT)
    axes.set_xlim(0, DOTS_PER_STRIP_LENGTH)
    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)

    axes_updater_gen = axes_updater(axes, reader)

    # Don't remove the "ani" binding below. Otherwise this animation
    # gets garbage collected.
    try:
        ani = animation.FuncAnimation(fig, lambda _: next(axes_updater_gen),
                                  interval=REFRESH_INTERVAL_MS)
    except StopIteration:
        pass

    plt.show()
    if print_timing_data:
        for p in reader.times:
            print(p)


def run_gui():

    parser = argparse.ArgumentParser(description='Run GUI for Olimex-EKG-EMG.')
    parser.add_argument('-p', '--port',
                        dest='port',
                        help='Port to which an Arduino is connected (eg. /dev/tty.usbmodem1411)')
    parser.add_argument('-f', '--file',
                        dest='file',
                        help='File to stream EXG data from. Loads entire file prior to display.')
    parser.add_argument('--list-mock-data',
                        action='store_true',
                        default=False,
                        dest='list_mock_data',
                        help='List all mock data files available.')
    parser.add_argument('--print-timing-data',
                        action='store_true',
                        default=False,
                        dest='print_timing_data',
                        help='File to stream EXG data from. Loads entire file prior to display.')
    args = parser.parse_args()

    if args.port:
        show_exg(args.port, print_timing_data=args.print_timing_data)

    elif args.file:
        data_dir, files = get_mock_data_list()
        if args.file in files:
            args.file = os.path.join(data_dir, args.file)
        if not os.path.exists(args.file):
            print('File at {} not found'.format(args.file))
            return
        show_exg(args.file, source_type='file', print_timing_data=args.print_timing_data)

    elif args.list_mock_data:
        data_dir, files = get_mock_data_list()
        if not data_dir:
            print('No mock data found. Please try reinstalling')
            return

        print('Mock data files are stored in {}'.format(data_dir))
        for file_ in files:
            print(file_)

    else:
        parser.print_help()


if __name__ == '__main__':
    # Performance testing
    import cProfile, pstats, io
    pr = cProfile.Profile()
    pr.enable()
    run_gui()
    pr.disable()
    s = io.StringIO()
    sortby = 'time'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(25)
    print(s.getvalue())

