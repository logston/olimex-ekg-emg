"""
This module defines several functions and classes for mocking a
serial port receiving Olimex-EKG-EMG (aka. EXG) packets.
"""
import random
import threading
import time

from olimex.constants import PACKET_SIZE, SYNC0, SYNC1, SAMPLE_FREQUENCY


def packet_data_generator():
    # uint16_t   data[6];  // 10-bit sample (= 0 - 1023) in big endian (Motorola) format.
    while True:
        byte_array = bytearray(random.randint(0, 255) for _ in range(12))
        yield byte_array


def packet_generator():
    """
    Return an EXG formatted packet that contains fake channel data.

    This generator produces fake packets of the form sent by the Olimex-EKG-EMG shield.
    """
    count = 0
    data_value_gen = packet_data_generator()
    while True:
        byte_array = bytearray((SYNC0, SYNC1, 2, count % 256))  # header bytes
        byte_array.extend(next(data_value_gen))  # data bytes
        byte_array.extend((1,))  # switches byte
        yield byte_array
        count += 1


class FakeSerialByteArray(object):
    """
    A class for mocking a serial.Serial object with data from a bytearray.
    """
    def __init__(self, byte_array, *args, **kwargs):
        self._buffer = byte_array
        self._pos = 0
        self._call_count = 0

    def __repr__(self):
        return '<FakeSerialByteArray {}>'.format(id(self))

    def inWaiting(self):
        self._call_count += 1
        # A random number I chose that
        # made the graph move at an acceptable
        # speed.
        if not self._call_count % 24:
            raise StopIteration

        left_in_buffer = len(self._buffer) - self._pos
        if left_in_buffer < PACKET_SIZE:
            return left_in_buffer

        return PACKET_SIZE

    def read(self, n=1):
        """
        Return n number of bytes.
        """
        new_pos = self._pos + n
        ret_val = self._buffer[self._pos:new_pos]
        self._pos = new_pos
        return ret_val

    def close(self):
        pass

