"""
This module defines a PacketStreamReader for reading packets
from an Olimex-EKG-EMG shield.


Details describing how an Olimex-EKG-EMG
shield packet is organized are below::

    ///////////////////////////////////////////////
    ////////// Packet Format Version 2 ////////////
    ///////////////////////////////////////////////
    17-byte packets are transmitted from Olimexino328 at 256Hz,
    using 1 start bit, 8 data bits, 1 stop bit, no parity,
    57600 bits per second.

    Minimial transmission speed is
    256Hz * sizeof(Olimexino328_packet) * 10 = 43520 bps.

    struct Olimexino328_packet
    {
      uint8_t    sync0;    // = 0xa5
      uint8_t    sync1;    // = 0x5a
      uint8_t    version;  // = 2 (packet version)
      uint8_t    count;    // packet counter. Increases by 1 each packet.
      uint16_t   data[6];  // 10-bit sample (= 0 - 1023) in big endian (Motorola) format.
      uint8_t    switches; // State of PD5 to PD2, in bits 3 to 0.
    };
"""
import serial
import time

from olimex.constants import SYNC0, SYNC1, PACKET_SIZE, PACKET_SLICES, DEFAULT_BAUDRATE
from olimex.utils import calculate_values_from_packet_data


class PacketStreamReader(object):
    """
    Instantiations of this class are iterators and can be passed to the
    :py:func:`next` function to retrieve the next available Olimex-EKG-EMG packet.

    For example::

        reader = PacketStreamReader('/path/to/port')
        packet = next(reader)
    """

    def __init__(self, port):
        self._serial = None
        self._open_serial_connection(port)

    def _open_serial_connection(self, port):
        self._serial = serial.Serial(port, DEFAULT_BAUDRATE)
        if not self._serial:
            raise serial.SerialException('Unable to open port {}'.format(port))

    def _get_next_packet(self):
        byte0, byte1 = None, None

        while byte0 != SYNC0 or byte1 != SYNC1:  # Looking for  b'\xa5', b'Z'
            # If we don't have enough data to do ALL of the following,
            # return None.
            #   - Move current byte 1 into byte0 position
            #   - Read a new byte into byte1  (1 byte)
            #   - Read the rest of a packet into a buffer (PACKET_SIZE - 2 bytes)
            # We need at least (PACKET_SIZE - 2) + 1 bytes before
            # attempting to get the next packet.
            if self._serial.inWaiting() < PACKET_SIZE - 1:
                return None

            byte0, byte1 = byte1, self._serial.read()
        
        # read 15 bytes and parse result
        buff = bytearray()
        buff.extend((ord(byte0), ord(byte1)))
        for _ in range(PACKET_SIZE - 2):
            buff.extend((ord(self._serial.read()),))
        return buff

    def _get_next_packet_value(self):
        packet = self._get_next_packet()
        if packet is None:
            return None
        data = packet[PACKET_SLICES['data']]
        return calculate_values_from_packet_data(data)

    @property
    def packets_in_waiting(self):
        return self._serial.inWaiting() // PACKET_SIZE

    def __iter__(self):
        return self

    def __next__(self):
        return self._get_next_packet_value()

    def __del__(self):
        if self._serial:
            self._serial.close()
