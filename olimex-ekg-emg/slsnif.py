import serial

ser = serial.Serial(port='/dev/tty.usbmodem1421', baudrate=57600)

array = bytearray()

while True:
    try:
        if ser.inWaiting():
            print(ser.inWaiting())
            array.extend(ser.read())
    except KeyboardInterrupt:
        break

with open('/Users/paul/Code/python/olimex-ekg-emg/olimex-ekg-emg/bytes.txt', 'wb') as fd:
    fd.write(array)
