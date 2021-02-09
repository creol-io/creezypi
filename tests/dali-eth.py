
import json
import time
import logging
import getopt
import sys
import socket

import serial

#


ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate=19200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1,
)

from web3 import Web3, HTTPProvider,WebsocketProvider

infura_wss_test = WebsocketProvider("wss://rinkeby.infura.io/ws/v3/d1170d8dd0ba484b9776ed4aec0f8d3a")
web3 = Web3([infura_wss_test])

if web3.isConnected():
	print("wss connection successful")
else:
	print("Connection Error: Please check settings")

LEDContractABI =  json.loads('[{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"newState","type":"bool"}],"name":"updateState","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"defaultState","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"updatedState","type":"bool"}],"name":"stateUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"constant":true,"inputs":[],"name":"currentState","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"isOwner","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]')
LEDAddress = '0x5e9eE98a6B32088F7cC5a0c6556b0F0E4d3E98D0'
LEDState = web3.eth.contract(address=LEDAddress, abi=LEDContractABI)


print("LEDContract Loaded at", LEDAddress)
listener_enable = True
currentLEDState = LEDState.functions.currentState().call()
while listener_enable:
	print("Listening")
	print("Checking State")
	checkState = LEDState.functions.currentState().call()
	if currentLEDState != checkState:
		print("New State On Chain, Updating profile")
		#Send DALI Packet Here
		print("Sending DALI")
		if checkState == True:
			print("Sending ON")
			ser.write('hFE80\n')
		else:
			print("Sending Off")
			ser.write('hFE00\n')
		currentLEDState = checkState
	else:
		#delay to next block
		time.sleep(2)
