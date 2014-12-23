import argparse
import os

import serial

from olimex.constants import DEFAULT_BAUDRATE


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def read_raw_data(port, logfile=None):
    ser = serial.Serial(port, baudrate=DEFAULT_BAUDRATE)
    array = bytearray()
    while True:
        try:
            if ser.inWaiting():
                data = ser.read()
                if logfile:
                    array.extend(data)
                print(data, end='', flush=True)
        except KeyboardInterrupt:
            if logfile:
                print('\nDumping data to disk...', end='', flush=True)
                with open(os.path.join(CURRENT_DIR, logfile), 'wb') as fd:
                    fd.write(array)
                print('Done.')
            break


def slsnif():
    """
    [-l <logfile>] ([--log <logfile>])
    File to direct output to. Output is sent to stdout by default.
    """
    parser = argparse.ArgumentParser(description='Serial line sniffer')

    parser.add_argument('port',
                        help='Port to sniff data from.')
    parser.add_argument('-l', '--log',
                        dest='logfile',
                        help='File to log serial data to. '
                             'Path should be relative to slsnif.py')
    args = parser.parse_args()

    read_raw_data(args.port, args.logfile)

if __name__ == '__main__':
    slsnif()
