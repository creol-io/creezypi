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


while 1 :
        text = input("Which DALI address ( 0-63, 127=all ) : ")
        address = int(text)*2
        text = raw_input("What Level ( 0-254) : ")
        level = int(text)

        ser.write(('h%02X\n%02X\n'%(address, level)).encode())   # send level
        time.sleep(.1)

