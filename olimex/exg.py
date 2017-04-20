"""
This module defines a PacketStreamReader for reading packets
from an Olimex-EKG-EMG shield.


Details describing how an Olimex-EKG-EMG
shield packet is organized are below::

    ///////////////////////////////////////////////
    ////////// Packet Format Version 2 ////////////
    ///////////////////////////////////////////////
    // 17-byte packets are transmitted from Olimexino328 at 256Hz,
    // using 1 start bit, 8 data bits, 1 stop bit, no parity.

    // Minimial Transmission Speed
    // A sample is taken every 8ms (ie. 125 samples per second)
    // 125 samples/s * sizeof(Olimexino328_packet) = 2,125 bytes per second
    // 2125 bytes per second = 17,000 bits per second.
    // 2.125 kBps (I think we can manage that :)
    // 7,650 kB per hour ~ 7.5M MB per hour

    struct Olimexino328_packet
    {
      uint8_t	sync0;		// = 0xa5
      uint8_t	sync1;		// = 0x5a
      uint8_t	version;	// = 2 (packet version)
      uint8_t	count;		// packet counter. Increases by 1 each packet.
      uint16_t	data[6];	// 10-bit sample (= 0 - 1023) in big endian (Motorola) format.
      uint8_t	switches;	// State of PD5 to PD2, in bits 3 to 0.
    };
"""
import time

from olimex.constants import PACKET_SIZE, PACKET_SLICES, SAMPLE_FREQUENCY, SYNC0, SYNC1
from olimex.utils import calculate_values_from_packet_data


class PacketStreamReader:
    """
    Instantiations of this class are iterators and can be passed to the
    :py:func:`next` function to retrieve the next available Olimex-EKG-EMG packet.

    For example::

        serial = serial.Serial(port, 115200)
        reader = PacketStreamReader(serial)
        packet = next(reader)
    """
    def __init__(self, serial):
        self._serial = serial
        # data members for tracking performance
        self._packet_index = 0
        self.start_time = time.perf_counter()
        self.times = []
        self.ret_none_count = 0

    def _get_next_packet(self):
        byte0, byte1 = 0, 0

        while byte0 != SYNC0 or byte1 != SYNC1:
            # If we don't have enough data to do ALL of the following,
            # return None.
            #   - Move current byte 1 into byte0 position
            #   - Read a new byte into byte1  (1 byte)
            #   - Read the rest of a packet into a buffer (PACKET_SIZE - 2 bytes)
            # We need at least (PACKET_SIZE - 2) + 1 bytes before
            # attempting to get the next packet.
            in_waiting = self._serial.inWaiting()
            if in_waiting < PACKET_SIZE - 1:
                return None
            byte0, byte1 = byte1, self._serial.read()

        buff = bytearray()
        buff.append(ord(byte0))
        buff.append(ord(byte1))
        # read 15 more bytes and parse result
        buff.extend(self._serial.read(PACKET_SIZE - 2))
        return buff

    def _get_next_packet_values(self):
        packet = self._get_next_packet()
        if packet is None:
            return None
        self._packet_index += 1
        data = packet[PACKET_SLICES['data']]
        return calculate_values_from_packet_data(data)

    @property
    def packets_in_waiting(self):
        return self._serial.inWaiting() // PACKET_SIZE

    def __iter__(self):
        return self

    def __next__(self):
        if not self._packet_index % SAMPLE_FREQUENCY:
            self.times.append(time.perf_counter() - self.start_time)

        values = self._get_next_packet_values()

        if values is None:
            self.ret_none_count += 1
            if self.ret_none_count >= 1000:
                raise StopIteration
        else:
            self.ret_none_count = 0
 
        return values

    def __del__(self):
        if self._serial:
            self._serial.close()

