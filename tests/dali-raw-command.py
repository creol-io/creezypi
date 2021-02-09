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
        input_type = input("Input Type h (16-bit) , t (16-bit Twice) , j (8-bit) , l (24-bit), d Power, v Version: \n")
        address = input("Raw Hex Command/Address: \n")
        command = input("Raw Hex: \n")

        ser.write((input_type+address+command+"\n").encode())   # send level
        time.sleep(.1)

