"""
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

NUMCHANNELS = 6
HEADERLEN = 4
PACKET_SIZE = (NUMCHANNELS * 2 + HEADERLEN + 1)
SAMPLE_FREQUENCY = 256  # ADC sampling rate 256
SYNC0 = 0xa5
SYNC1 = 0x5a
DEFAULT_BAUDRATE = 57600


class PacketStreamReader(object):
    def __init__(self, port, **kwargs):
        self.serial = None
        self.open_serial_connection(port)
        if not self.serial:
            raise portNotOpenError

    def open_serial_connection(self, port):
        self.serial = serial.Serial(port)

    def _get_next_packet(self):
        if self.serial.inWaiting() < PACKET_SIZE:
            return -1, None

        byte0 = None
        byte1 = None
        
        while byte0 != SYNC0 or byte1 != SYNC1: 
            if self.serial.inWaiting() < PACKET_SIZE: 
                return -1, None
            else:
                byte0 = byte1
                byte1 = self.serial.read()
        
        # read 15 bytes and parse result
        buff = bytearray()
        buff.extend(byte0)
        buff.extend(byte1)
        for _ in range(PACKET_SIZE - 2):
            buff.extend(self.serial.read())
        return buff

    def _parse_packet(self, packet):
        sync0 = packet[0]
        sync1 = packet[1]
        version = packet[2]
        count = packet[3]
        data = packet[4:16]
        switches = packet[16]

        return data

    def _calculate_value_from_packet_data(self, data):
        return data

    def get_next_packet_value(self):
        packet = self._get_next_packet()
        data = self._parse_packet(packet)
        return self._calculate_value_from_packet_data(data)

    def __iter__(self):
        return self

    def __next__(self):
        return None

    def __del__(self):
        if self.serial:
            self.serial.close()
        

if __name__ == '__main__': 
    import unittest

    class PacketStreamReaderTestCase(unittest.TestCase):
        def test___init__(self):
            # trying to open a non-existant port raises exception
            with self.assertRaises(serial.serialutil.SerialException):
                PacketStreamReader('/fake/port/noop/')

        def test__get_next_packet(self):
            raise NotImplementedError

        def test__parse_packet(self):
            raise NotImplementedError

        def test__calculate_value_from_packet_data(self):
            raise NotImplementedError

        def test_get_next_packet_value(self):
            raise NotImplementedError

        def test___next__(self):
            raise NotImplementedError

    unittest.main()
