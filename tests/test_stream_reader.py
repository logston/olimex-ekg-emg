import random
import unittest
from olimex.constants import PACKET_SLICES
from olimex.exg import PacketStreamReader
from olimex.mock import packet_generator, FakeSerialByteArray
from olimex.utils import calculate_values_from_packet_data


class PacketStreamReaderTestCase(unittest.TestCase):
    def test__get_next_packet(self):
        byte_array = bytearray()
        # add some noise
        byte_array.extend((random.randint(0, 255) for _ in range(5)))
        packet_gen = packet_generator()
        packet1 = next(packet_gen)
        byte_array.extend(packet1)
        packet2 = next(packet_gen)
        byte_array.extend(packet2)
        packet3 = next(packet_gen)
        byte_array.extend(packet3)

        serial = FakeSerialByteArray(byte_array)
        reader = PacketStreamReader(serial)
        self.assertEqual(packet1, reader._get_next_packet())
        self.assertEqual(packet2, reader._get_next_packet())
        self.assertEqual(packet3, reader._get_next_packet())

    def test_get_next_packet_values(self):
        byte_array = bytearray()
        # add some noise
        byte_array.extend((random.randint(0, 255) for _ in range(5)))
        packet_gen = packet_generator()

        packet1 = next(packet_gen)
        byte_array.extend(packet1)
        packet1_data = packet1[PACKET_SLICES['data']]
        packet1_value = calculate_values_from_packet_data(packet1_data)

        packet2 = next(packet_gen)
        byte_array.extend(packet2)
        packet2_data = packet2[PACKET_SLICES['data']]
        packet2_value = calculate_values_from_packet_data(packet2_data)

        serial = FakeSerialByteArray(byte_array)
        reader = PacketStreamReader(serial)
        self.assertEqual(packet1_value, reader._get_next_packet_values())
        self.assertEqual(packet2_value, next(reader))


class UtilsTestCase(unittest.TestCase):
    def test_calculate_value_from_packet_data(self):
        values_to_assert_equal = (
            ([0, 37, 247, 387, 432, 511],
             bytearray((0x00, 0x00, 0x00, 0x25, 0x00, 0xf7, 0x01, 0x83, 0x01, 0xb0, 0x01, 0xff))),
            ([512, 678, 750, 832, 900, 1023],
             bytearray((0x02, 0x00, 0x02, 0xa6, 0x02, 0xee, 0x03, 0x40, 0x03, 0x84, 0x03, 0xff))),
        )
        for value_pair in values_to_assert_equal:
            values, data = value_pair[0], value_pair[1]
            self.assertEqual(values, calculate_values_from_packet_data(data))
