import os

import serial


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def read_raw_data(port='/dev/tty.usbmodem1421'):
    ser = serial.Serial(port, baudrate=57600)

    array = bytearray()

    while True:
        try:
            if ser.inWaiting():
                print(ser.inWaiting())
                array.extend(ser.read())
        except KeyboardInterrupt:
            break

    with open(os.path.join(CURRENT_DIR, 'bytes.bin'), 'wb') as fd:
        fd.write(array)
