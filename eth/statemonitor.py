# Title: state-monitor
#
#   _____ _        _         __  __             _ _
#  / ____| |      | |       |  \/  |           (_) |
# | (___ | |_ __ _| |_ ___  | \  / | ___  _ __  _| |_ ___  _ __
#  \___ \| __/ _` | __/ _ \ | |\/| |/ _ \| '_ \| | __/ _ \| '__|
#  ____) | || (_| | ||  __/ | |  | | (_) | | | | | || (_) | |
#|_____/ \__\__,_|\__\___| |_|  |_|\___/|_| |_|_|\__\___/|_|
#
#
# Author: Joshua Bijak
# Date:  11/06/2019
# Desc:  Interface for Querying Ethereum Blockchain for LED/Room States
# Changelog: 11/06/2019  - First Write
# 02/09/2021 - Polish for public release


import json
import time
import logging
import getopt
import sys
import socket

import serial
import os

from concurrent import futures

from web3 import Web3, HTTPProvider, WebsocketProvider


class StateMonitor:

	infura_dev = "INFURA_DEV_KEY_HERE"
	infura_prod = "INFURA_PROD_KEY_HERE"

	mainnetid = 0
	rinkebyid = 4
	mumbaiid = 80001

	web3 = 0
	RoomData = 0
	RoomABI = 0
	DeployedRoomAddressRinkeby = 0
	RoomState = 0
	VCUOffsetData = 0
	VCUOffsetABI = 0
	DeployedVCUAddressRinkeby = 0
	VCUOffset = 0
	creezyLeader = 0
	LEDAddresses = 0

	def __init__(self, infura_key=infura_dev, networkid=mumbaiid, defaultWeb3Account=""):
		print("Initializing Monitor... \n")

		infura_wss = 0
		if (networkid == 0):
			print("Connecting Websocket to Infura Mainnet...")
			infura_wss = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws/v3/"+infura_key, websocket_kwargs={'timeout': 120}))
		elif(networkid == 4):
			print("Connecting Websocket to Infura Rinkeby...")
			infura_wss = Web3(Web3.WebsocketProvider("wss://rinkeby.infura.io/ws/v3/" + infura_key, websocket_kwargs={'timeout': 120}))
		elif(networkid == 80001):
			print("Connecting WSS to Mumbai RPC...")
			infura_wss = Web3(Web3.WebsocketProvider("wss://ws-mumbai.matic.today", websocket_kwargs={'timeout': 120}))
		if(infura_wss != 0):

			if infura_wss.isConnected():
				print("wss connection successful")
				self.web3 = infura_wss
				self.web3.eth.defaultAccount = defaultWeb3Account
			else:
				print("Connection Error: Please check settings")

	def init_room_state(self):
		print("Initializing Room State and Contracts")
		dirname = os.path.dirname(__file__)
		RoomStateFile = os.path.join(dirname, '../creol-eth/build/contracts/RoomState.json')
		# with open("../creol-eth/contracts/build/contracts/RoomState.json") as RoomStateContractFile:
		with open(RoomStateFile) as RoomStateContractFile:
			self.RoomData = json.load(RoomStateContractFile)
			self.RoomABI = self.RoomData['abi']

	def check_web3_connection(self):
		if self.web3 != 0:
			# Check Web3 Connection
			try:
				if self.web3.isConnected():
					return True
			except futures.TimeoutError:
					print("wss connection is closed. Reopening...")
					self.__init__()
					try:
						if self.web3.isConnected():
							print("Reconnect Success!")
							return True
					except:
						print("Reconnect Failed")
						return False

	def connect_room_state(self, roomAddress, creezy_leader):
		"""
		Connects the statemonitor to the Room supplied by the roomAddress variable
		Pulls the current LEDs in said room afterwards.
		:param roomAddress: Room Contract address to connect to
		:param creezy_leader: String of the name of Creezy Lead device.
		:return: no return
		"""
		print("Connecting Room State...\n")
		self.DeployedRoomAddressRinkeby = roomAddress
		self.RoomState = self.web3.eth.contract(address=self.DeployedRoomAddressRinkeby, abi=self.RoomABI)
		print("Room Contract loaded at ", roomAddress)

		print("Fetching Room Leader...")
		print("RoomState functions: ", self.RoomState.functions)
		result = self.RoomState.functions.groupNametoParentCreezyPi(creezy_leader).call({'from': self.web3.eth.defaultAccount})
		print("Creezy Coap Address: ", result[0],"\ncreezyID: ", result[1], "\nNumber of LEDs: ", result[2], "\nNumber of Universes: ", result[3], "\nis Active?: ",result[4])

		result = self.RoomState.functions.getGroupAddresses(creezy_leader).call()
		count = 0
		LEDAddressesList = list()
		for i in result:
			print("LED Address of ", count, " is ", i)
			LEDAddressesList.append(i)
			count += 1
		self.LEDAddresses = LEDAddressesList

	def init_VCU_Offsetter(self):
		print("Initializing Offsetter Functionality")
		dirname = os.path.dirname(__file__)
		VCUOffsetFile = os.path.join(dirname, '../creol-eth/contracts/build/contracts/VCUOffset.json')
		with open(VCUOffsetFile) as VCUOffsetContractFile:
			self.VCUOffsetData = json.load(VCUOffsetContractFile)
			self.VCUOffsetABI = self.VCUOffsetData['abi']

	def connect_VCU_Offsetter(self, VCUOffsetAddress):
		print("Connecting VCU Offsetter...\n")
		self.DeployedVCUAddressRinkeby = VCUOffsetAddress
		self.VCUOffset = self.web3.eth.contract(address=self.DeployedVCUAddressRinkeby, abi=self.VCUOffsetABI)
		print("VCUOffset Contract loaded at ", VCUOffsetAddress)


