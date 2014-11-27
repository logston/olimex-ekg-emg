"""
This module defines constants used throughout this package.
"""

NUMCHANNELS = 6
HEADERLEN = 4
PACKET_SIZE = (NUMCHANNELS * 2 + HEADERLEN + 1)
SAMPLE_FREQUENCY = 256  # ADC sampling rate 256
SYNC0 = b'\xa5'  # 0xa5, 165
SYNC1 = b'Z'  # 0x5a, 90

DEFAULT_BAUDRATE = 57600


PACKET_SLICES = {
    'sync0': slice(0, 1),
    'sync1': slice(1, 2),
    'version': slice(2, 3),
    'count': slice(3, 4),
    'data': slice(4, 16),
    'switches': slice(16)
}
