"""
For proper communication packet format given below have to be supported:
///////////////////////////////////////////////
////////// Packet Format Version 2 ////////////
///////////////////////////////////////////////
// 17-byte packets are transmitted from Olimexino328 at 256Hz,
// using 1 start bit, 8 data bits, 1 stop bit, no parity, 57600 bits per second.

// Minimial transmission speed is 256Hz * sizeof(Olimexino328_packet) * 10 = 43520 bps.

struct Olimexino328_packet
{
  uint8_t       sync0;          // = 0xa5
  uint8_t       sync1;          // = 0x5a
  uint8_t       version;        // = 2 (packet version)
  uint8_t       count;          // packet counter. Increases by 1 each packet.
  uint16_t      data[6];        // 10-bit sample (= 0 - 1023) in big endian (Motorola) format.
  uint8_t       switches;       // State of PD5 to PD2, in bits 3 to 0.
};
*/
"""
import serial 

SYNC0 = 0xa5
SYNC1 = 0x5a
PACKET_SIZE = 17


def parse_packet(packet):
    sync0 = packet[0]
    sync1 = packet[1]

    version = packet[2]
    count = packet[3]
    data = packet[4:16]
    switches = packet[16]
    return version 


if __name__ == '__main__': 
    S = serial.Serial('/dev/tty.usbmodem1411', 57600)
    print (S.name)
    byte0, byte1 = None, None
    while True:
        byte0 = byte1
        byte1 = S.read()
        if byte0 == SYNC0 and byte1 == SYNC1:
            S.read(PACKET_SIZE - 2)
        break

    while True:      
        print (parse_packet(S.read(PACKET_SIZE)))
