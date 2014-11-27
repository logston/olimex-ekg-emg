"""
This module prints each packet in a file located at ../mock-data/bytes.bin
"""
import os
from olimex.constants import PACKET_SLICES

from olimex.exg import PacketStreamReader
from olimex.mock import SerialMocked
from olimex.utils import calculate_values_from_packet_data


olimex_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def print_packets():
    with SerialMocked(os.path.join(olimex_root, 'mock-data', 'bytes.bin')):
        reader = PacketStreamReader('/fake/port')

        next_packet = reader._get_next_packet()
        while next_packet:
            data = next_packet[PACKET_SLICES['data']]
            values = calculate_values_from_packet_data(data)
            print("{0: <60} {1: <20}".format(str(data), str(values)))
            next_packet = reader._get_next_packet()


if __name__ == '__main__':
    print_packets()