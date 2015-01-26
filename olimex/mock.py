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

    def __repr__(self):
        return '<FakeSerialByteArray {}>'.format(id(self))

    def inWaiting(self):
        return len(self._buffer)

    def read(self):
        """
        Return one byte.
        """
        return self._buffer.pop(0)

    def close(self):
        pass


class FakeSerialFromFile(object):
    """
    A class for mocking a :py:class:`serial.Serial` object with data from a file.
    """
    def __init__(self, file_path,
                 sample_frequency=SAMPLE_FREQUENCY,
                 *args, **kwargs):
        self.file_path = file_path
        self._buffer = bytearray()
        self._bytes_per_second = sample_frequency * PACKET_SIZE
        self._seconds_per_byte = 1 / self._bytes_per_second
        self._max_in_waiting = 1048576  # Store up to 1 MB in ram.
        self._stop_thread_signal = False
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._read_data_from_file, args=(file_path,))

    def __repr__(self):
        return '<FakeSerialFromFile: {file_path}>'.format(file_path=self.file_path)

    def start(self):
        self._thread.start()

    def _read_data_from_file(self, file_path):
        with open(file_path, 'rb') as fd:
            while True:
                # TODO ask if this is bad, checking value outside of lock
                if self._stop_thread_signal:
                    return

                if self.inWaiting() < self._max_in_waiting:
                    byte = fd.read(1)
                    with self._lock:
                        self._buffer.extend(byte)
                time.sleep(self._seconds_per_byte)

    def inWaiting(self):
        with self._lock:
            len_ = len(self._buffer)
        return len_

    def read(self, *args, **kwargs):
        """
        Return one byte from buffer.
        """
        if not self.inWaiting():
            return bytes()

        try:
            with self._lock:
                byte_ = self._buffer.pop(0)
            return byte_
        except IndexError:
            raise StopIteration

    def close(self):
        self._stop_thread_signal = True
        for _ in range(3):
            time.sleep(10 * self._seconds_per_byte)
            if self._thread.isAlive():
                print('Thread failed to die. Waiting...')
            else:
                return
        raise SystemExit('Thread failed to die. Killing main process.')


class FakeSerialTimedByteArray(object):
    """
    A class for mocking a serial.Serial object with data from a bytearray.
    """

    def __init__(self, byte_array, sample_frequency=SAMPLE_FREQUENCY, *args, **kwargs):
        self._buffer = byte_array
        self._last_read = time.monotonic()
        self._bytes_per_second = sample_frequency * PACKET_SIZE
        self._seconds_per_byte = 1 / self._bytes_per_second
        self._ready_bytes = bytearray()

    def __repr__(self):
        return '<FakeSerialTimedByteArray {}>'.format(id(self))

    def inWaiting(self):
        return len(self._buffer)

    def read(self):
        """
        Return one byte.
        """
        if not self._ready_bytes:
            cur_time = time.monotonic()
            time_diff = cur_time - self._last_read
            if time_diff < 1000 * self._seconds_per_byte:
                return bytes('\x00', encoding='utf8')
            byte_count = int(time_diff * self._bytes_per_second)
            self._last_read = cur_time
            self._ready_bytes = bytearray(self._buffer.pop(0) for _ in range(byte_count))
        return self._ready_bytes.pop(0)

    def close(self):
        pass

