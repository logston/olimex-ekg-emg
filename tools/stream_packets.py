"""
This module prints each packet in a file located at ../mock-data/bytes.bin
"""
import time
from olimex.constants import PACKET_SLICES

from olimex.exg import PacketStreamReader
from olimex.utils import calculate_values_from_packet_data


def stream_packets():

    reader = PacketStreamReader('/dev/tty.usbmodem1411')

    packet_num = 0
    while True:
        next_packet = reader._get_next_packet()
        packet_num += 1
        if next_packet:
            data = next_packet[PACKET_SLICES['data']]
            values = calculate_values_from_packet_data(data)
            values = list(map(lambda x: x * 0.5, values))
            values.append(packet_num)
            print("{}".format(','.join(map(str, values))))
        else:
            print("No packet available")
        time.sleep(1/256)


if __name__ == '__main__':
    stream_packets()