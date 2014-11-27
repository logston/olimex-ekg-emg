"""
This module defines several functions and classes for mocking a
serial port which is receiving Olimex-EKG-EMG packets.
"""
import random
import sys

from olimex.constants import PACKET_SIZE, SYNC0, SYNC1


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


def fake_serial_class_factory(mock_data_source):
    """
    Return a serial.Serial like object.

    A factory for creating serial.Serial like objects. This objects
    can be used for testing other logic within in this package.
    :param mock_data_source:
    """
    if isinstance(mock_data_source, str):
        file_path = mock_data_source

        class FakeSerialFromFile(object):
            """
            A class for mocking a serial.Serial object with data from a file.
            """
            def __init__(self, *args, **kwargs):
                self.fd = open(file_path, 'rb')
                self._buffer = bytearray()
                self._in_waiting = 0

                self._read_fake_data()

            def _read_fake_data(self):
                for _ in range(PACKET_SIZE * 10):
                    byte = self.fd.read(1)
                    if not byte:
                        break
                    self._buffer.extend(byte)
                    self._in_waiting += 1

            def inWaiting(self):
                return self._in_waiting

            def read(self):
                """
                Return one byte.
                """
                self._in_waiting -= 1
                if self._in_waiting < PACKET_SIZE:
                    self._read_fake_data()
                return self._buffer.pop(0)

            def close(self):
                self.fd.close()

        return FakeSerialFromFile
    elif isinstance(mock_data_source, bytearray):
        class FakeSerialByteArray(object):
            """
            A class for mocking a serial.Serial object with data from a bytearray.
            """

            def __init__(self, *args, **kwargs):
                self._buffer = mock_data_source
                self._in_waiting = len(mock_data_source)

            def inWaiting(self):
                return self._in_waiting

            def read(self):
                """
                Return one byte.
                """
                self._in_waiting -= 1
                return self._buffer.pop(0)

            def close(self):
                pass

        return FakeSerialByteArray


class SerialMocked(object):
    """
    A context manager for mocking serial.Serial objects during testing.
    """
    def __init__(self, mock_data_source):
        self.fake_serial_class = fake_serial_class_factory(mock_data_source)

    def __enter__(self):
        """
        Replace real serial.Serial class with ``FakeSerial``.
        """
        self.real_serial_class = sys.modules['serial'].Serial
        sys.modules['serial'].Serial = self.fake_serial_class

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.modules['serial'].Serial = self.real_serial_class