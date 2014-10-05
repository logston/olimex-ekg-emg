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
import io
from queue import Queue, Empty
import time
from threading import Thread

import serial 

NUMCHANNELS = 6
HEADERLEN = 4
PACKET_SIZE = (NUMCHANNELS * 2 + HEADERLEN + 1)
SAMPLE_FREQUENCY = 256  # ADC sampling rate 256
SYNC0 = 0xa5
SYNC1 = 0x5a
DEFAULT_BAUDRATE = 57600


def parse_packet(packet):
    packet = [packet.read(1) for _ in range(PACKET_SIZE)]
    sync0 = packet[0]
    sync1 = packet[1]

    version = packet[2]
    count = packet[3]
    data = packet[4:16]
    switches = packet[16]
    return version 


class UnexpectedEndOfStream(Exception): pass


class NonBlockingStreamReader:

    def __init__(self, stream):
        """ 
        :param stream: the stream to read from. ie. serial port
        """
        self._stream = stream
        self._queue = Queue()

        self._thread = Thread(
            target = self._populate_queue,
            args = (self._stream, self._queue)
        )
        self._thread.daemon = True
        self._thread.start()  # start collecting lines from the stream
    
    def _populate_queue(self, stream, queue):
        """
        Collect one byte from ``stream`` and put it in ``queue``.
        """
        while True:
            byte = stream.read()
            if byte:
                queue.put(byte)
            else:
                raise UnexpectedEndOfStream

    def read_byte(self, timeout=None):
        try:
            return self._queue.get(block=timeout is not None, timeout = timeout)
        except Empty:
            return None


if __name__ == '__main__': 
    S = serial.Serial('/dev/tty.usbmodem1411', DEFAULT_BAUDRATE)
    print (S.name)

    nbsr = NonBlockingStreamReader(S)
   
    time.sleep(1)
    
    byte0, byte1 = None, None
    
    while True:
        byte0 = byte1
        byte1 = nbsr.read_byte()
        if byte0 == SYNC0 and byte1 == SYNC1:
            for _ in range(PACKET_SIZE - 2):
                nbsr.read_byte()
        break
    
    while True:      
        buffer_ = io.BytesIO()
        for _ in range(PACKET_SIZE):
            buffer_.write(nbsr.read_byte())
        print (parse_packet(buffer_))

