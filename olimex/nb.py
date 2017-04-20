import os

from bokeh.client import push_session
from bokeh.io import curdoc
from bokeh.plotting import figure
import numpy as np
from olimex.mock import FakeSerialByteArray
from olimex.exg import PacketStreamReader
from olimex.utils import get_mock_data_list
import scipy.ndimage
import serial

from olimex.constants import DEFAULT_BAUDRATE, SAMPLE_FREQUENCY

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

INITIAL_VOLTAGE = DOTS_PER_STRIP_HEIGHT / 2


def get_new_data_points(packet_reader):
    """
    Return all data points in the buffer waiting to be displayed.

    In between refreshes of the graph, data points will be
    read into a waiting buffer where they are held before
    they are displayed during the next refresh. The packet
    reader is responsible for managing that buffer.
    """
    while True:
        new_data = []
        while True:
            try:
                channel_values = next(packet_reader)
            except StopIteration:
                break

            if channel_values:
                channel_1, *_ = channel_values
                new_data.append(channel_1)

        new_data = scipy.ndimage.zoom(
            new_data,
            DOTS_PER_SECOND / SAMPLE_FREQUENCY,
            order=0
        )
        yield new_data


def exg(source):
    if source.endswith('.bin'):
        data_dir, data_list = get_mock_data_list()
        source = os.path.join(data_dir, source)
        print('Loading data...', end='', flush=True)
        with open(source, 'rb') as fd:
            buff = bytearray(fd.read())
        serial_obj = FakeSerialByteArray(buff)
        print('Done.', flush=True)

    else:
        serial_obj = serial.Serial(source, baudrate=DEFAULT_BAUDRATE)

    reader = PacketStreamReader(serial_obj)
    new_data_gen = get_new_data_points(reader)

    p = figure(
        x_range=(0, 1024),
        y_range=(0, 1024),
        plot_width=1024, 
        plot_height=400,
        tools=[],
    )
    line = p.line(
        x=tuple(range(1024)), 
        y=tuple(512 for _ in range(1024))
    )

    ds = line.data_source

    def update():
        data = next(new_data_gen)

        new_y = tuple(ds.data['y']) + tuple(data)
        new_y = new_y[-1024:]

        new_x = tuple(range(len(new_y)))

        ds.data.update(x=new_x, y=new_y)

    curdoc().add_periodic_callback(update, 30)

    # open a session to keep our local document in sync with server
    session = push_session(curdoc())
    session.show(p) # open the document in a browser
    try:
        session.loop_until_closed() # run forever
    finally:
        serial_obj.close()

