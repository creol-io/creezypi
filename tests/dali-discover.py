#
# program to read the info about all devices on a DALI bus
# loop from 0-63 to get on/off/level and dali type
#

import RPi.GPIO as GPIO
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

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
GPIO.setup(6, GPIO.IN)

print('\n      ATX LED Consultants Inc - Fixture Read UPC, Version, SN \n')

if GPIO.input(6) == 0:
    print('Power: Primary Power missing')
else:
    print('Power: Primary Power OK')

if GPIO.input(5) == 0:
    print('Power: Secondary Power missing')
else:
    print('Power: Secondary Power OK')

ser.write(('v\n').encode())  # lets get version number first
x = ser.read()
if x == "":
    print(' Missing Firmware \n')
    exit()

x = ser.read(2)
print('HW version: %s' % (x))
y = ser.read(2)
print('FW version: %s' % (y))
y = ser.read(1)

ser.write('d\n'.encode())  # now check if Power is good
x = ser.read(1).encode()
if x == 'D':
    y = ser.read(2)
    y = int(y, 16)
    if y == 0:
        print('DALI BUS: power is lost')
    if y == 1:
        print('DALI BUS: power is stuck high')
    if y == 2:
        print('DALI BUS: power is good')
    if y == 3:
        print('DALI BUS: power is not yet known')

print(' ')

printDebug = True

i = 0

while i < 64:
    # Clean Buffer First
    x = ser.read(100)
    print('Scan DALI bus address...: ' + str(i))
    # Convert to Address  (2* BitShift 1)
    a = (i * 2) + 1
    # Query  Actual Dim Level
    if printDebug:
        print("Query Status")
    ser.write(('h%02X90\n' % a).encode())
    x = ser.read(1)
    print("Response : "+str(x))
    if x.decode() == 'J':
        print("Response Received")
        x = ser.read(2)
        y = int(x, 16)
        x = ser.read(1)
        ser.write(('h%02XA6\n' % a).encode())
        x = ser.read(1)
        z = "  "
        if x == 'J':
            z = ser.read(2)
        x = ser.read(1)
        ser.write(('h%02X99\n' % a).encode())
        x = ser.read(1)
        dt = "  "
        if x == 'J':
            dt = ser.read(2)
        x = ser.read(1)
        print('address %2d is Model %s DT %s level %3d' % (i, z, dt, y))
    else:
        x = ser.read(1)
    i = i+1
