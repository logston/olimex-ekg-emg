"""
This module prints each packet in a file located at ../mock-data/bytes.bin
"""
import os
from olimex.constants import PACKET_SLICES

from olimex.exg import PacketStreamReader
from olimex.mock import FakeSerialFromFile
from olimex.utils import calculate_values_from_packet_data


olimex_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def print_packets():
    serial_obj = FakeSerialFromFile(os.path.join(olimex_root, 'mock-data', 'DATALOG.TXT'))
    serial_obj.start()
    reader = PacketStreamReader(serial_obj)

    packet = next(reader)
    while packet:
        data = packet[PACKET_SLICES['data']]
        values = calculate_values_from_packet_data(data)
        print("{0: <60} {1: <20}".format(str(data), str(values)))
        packet = next(reader)


if __name__ == '__main__':
    print_packets()