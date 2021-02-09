


"""
DALI Group Test. Test grouping commands of already established groups
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

"""
Fetch the groups from the BUS
"""
print("Fetching Groups...")
daliGroupTestBus.fetchDALIGroups()
print("Complete")

print("Testing groups with members...")

for i in range(16):
    if daliGroupTestBus.groups[i].numMembers != 0:
        print("Found members...")
        print("Group " +str(i)+"Off")
        daliGroupTestBus.controlgroup(i, 0)
        time.sleep(2)
        print("Group " + str(i) + "On")
        daliGroupTestBus.controlgroup(i, 254)
        time.sleep(2)
        print("Group " + str(i) + "Off")
        daliGroupTestBus.controlgroup(i, 0)
        time.sleep(2)

print("Group Test Complete")


