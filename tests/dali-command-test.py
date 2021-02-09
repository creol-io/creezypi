# Test the DALI bus
# first set all to 50%
# then to off
# then to 100%
# then to off
# then input the address to control
# then input the level
# send to bus
# loop to input

import time
import serial
import sys

ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate=19200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1,
)

ser.write(('hFE80\n').encode())  # all on 128
time.sleep(1)
ser.write(('hFE00\n').encode())  # all off
time.sleep(1)
ser.write(('hFEFE\n').encode())  # all on full
time.sleep(1)
ser.write(('hFE00\n').encode())  # all off
time.sleep(1)


while 1:
        text = input("Input Type h (16-bit) , t (16-bit Twice) , j (8-bit) , l (24-bit), d Query Power, v Query Version: \n")
        input_type = text
        address = int(input("Destination ?: 0-63: 127 All: \n"))*2
        command = int(input("What Command ( 0-254) : "))

        ser.write((input_type+'%02X%02X\n' % (address, command)).encode())   # send level
        time.sleep(.1)

