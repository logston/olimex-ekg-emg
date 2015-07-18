import argparse
import os
import time

import serial

from olimex.constants import DEFAULT_BAUDRATE


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def slsnif(port, logfile=None):
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Serial line sniffer')

    parser.add_argument('port',
                        help='Port to sniff data from.')
    parser.add_argument('-l', '--log',
                        dest='logfile',
                        help='File to log serial data to. '
                             'Path should be relative to slsnif.py')
    args = parser.parse_args()

    print('Stop program with CTRL + C')
    if args.logfile:
        print('Streaming data will be written to disk when program is stopped.')

    time.sleep(2)
    slsnif(args.port, args.logfile)

