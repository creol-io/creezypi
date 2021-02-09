
"""
DALI Loop Test. Test the viability of loops within DALI networks based on fade times.
"""


import serial
import sys
import os
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))


import dali_hat.daliCommands as daliCommands

"""
Initialize the BUS w extended commands
"""
print("Initializing the BUS with commands")
daliGroupTestBus = daliCommands.daliCommands()
print("Complete")

# Addresses to loop through
short_addr_loop = [42,50,60]
# dali setting to set them all to
fade_time_DALI = 7
lowbyte = '{0:0{1}X}'.format(fade_time_DALI, 2)

fade_times = [0, 0.7, 1.0, 1.4, 2.0, 2.8, 4.0, 5.6, 8.0, 11.3, 16.0, 22.6, 32.0, 45.2, 64.0, 90.0]

percent_truncate = 0.20
wait_percent = 0.80
# Send Off
daliGroupTestBus.daliSerialCommand.dali_send_16_cmd("FF","00", False)
daliGroupTestBus.daliSerialCommand.dali_read_bytes()
time.sleep(0.10)
# Set DTR
daliGroupTestBus.daliSerialCommand.dali_send_16_cmd("A3",lowbyte, False)
daliGroupTestBus.daliSerialCommand.dali_read_bytes()
time.sleep(0.10)

for i in range(len(short_addr_loop)):
	lowbyte = '{0:0{1}X}'.format(fade_time_DALI, 2)
	# Set DTR
	daliGroupTestBus.daliSerialCommand.dali_send_16_cmd("A3", lowbyte, False)
	daliGroupTestBus.daliSerialCommand.dali_read_bytes()
	time.sleep(0.10)
	# Send SET FADE DOWN And UP equal
	highbyte = (short_addr_loop[i] << 1) + 1
	highbyte = '{0:0{1}X}'.format(highbyte, 2)
	# Fade Down Set
	daliGroupTestBus.daliSerialCommand.dali_send_16_twice_cmd(highbyte,"2F", False)
	daliGroupTestBus.daliSerialCommand.dali_read_bytes()
	time.sleep(0.10)
	# Fade Up Set
	daliGroupTestBus.daliSerialCommand.dali_send_16_twice_cmd(highbyte, "2E", False)
	daliGroupTestBus.daliSerialCommand.dali_read_bytes()
	time.sleep(0.10)

print("Fade times set!")

print("Beginning Loop")

while True:
	for i in range(len(short_addr_loop)):
		highbyte = '{0:0{1}X}'.format(short_addr_loop[i], 2)
		# Turn On
		daliGroupTestBus.directcontrol_individual(highbyte, "FE",False)
		daliGroupTestBus.daliSerialCommand.dali_read_bytes()
		# Wait % of Fade Time
		time.sleep((fade_times[fade_time_DALI]*wait_percent))
		# Turn Off
		daliGroupTestBus.directcontrol_individual(highbyte, "00", False)
		daliGroupTestBus.daliSerialCommand.dali_read_bytes()


