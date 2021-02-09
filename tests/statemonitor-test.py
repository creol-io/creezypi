

import serial
import sys
import os
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

import eth.statemonitor as stateMonitor


print("Checking State monitor")
roomState = stateMonitor.StateMonitor()
print("Initializing Room State")
roomState.init_room_state()
print("Connecting Room State")
roomState.connect_room_state("0xE81D6403FC527F8C505b42101f4422180b56230F", "CreezyPi-2-Plymouth")