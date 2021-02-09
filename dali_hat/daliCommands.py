# Title: Dali Commands
#
#  _____          _      _____    _____                                          _
# |  __ \   /\   | |    |_   _|  / ____|                                        | |
# | |  | | /  \  | |      | |   | |     ___  _ __ ___  _ __ ___   __ _ _ __   __| |___
# | |  | |/ /\ \ | |      | |   | |    / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
# | |__| / ____ \| |____ _| |_  | |___| (_) | | | | | | | | | | | (_| | | | | (_| \__ \
# |_____/_/    \_\______|_____|  \_____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/
#
#
# Author: Joshua Bijak
# Date:  07/05/2019
# Desc:  Script Containing Usage of the DALI Bus class defined into easier functions
# Changelog: 07/05/2019 -  Initial Log.
#            Functions Pulled from latest list found here. https://atxled.com/pdf/AL-WS-DR2.pdf
#			 Functions structure setup like so 	https://atxled.com/pdf/AL-DALI-HAT.pdf

import time

import dali_hat.daliBus as daliSerial

import dali_hat.daliGroup as daliGroup


class daliCommands:

	numberofgroups = 0
	DEBUG = True
	groups = []
	daliSerialCommand = 0

	def __init__(self):
		"""
		Initializes the DALI Commands Module for simplified DALI Commands
		"""
		print("Commands now initialized... all DALI commands are now available")
		self.daliSerialCommand = daliSerial.DaliBus()
		i = 0
		# TODO: Make this dynamic in case of DALI hat 4
		print("Initializing Groups")
		while i < 16:
			self.groups.append(daliGroup.daliGroup(0, i, []))
			i = i + 1

	def createDALIGroup(self, short_address_list):
		"""
		Creates DALI group from Short Address List
		:param short_address_list: List of Short addresses as ints 0-63
		:return: returns numbers of DALI Groups
		"""
		Yselect = bin(128)

		if self.numberofgroups >= 15:
			print("Already 16 Groups")
			return -1

		for i in short_address_list:
			short_convert = '{0:0{1}X}'.format(short_address_list[i], 2)
			if self.DEBUG:
				print("Adding Short Adddress: "+short_convert+' to Group: '+str(self.numberofgroups))

			self.addtoDALIGroup(self.numberofgroups, short_address_list[i])

		self.groups[self.numberofgroups] = daliGroup.daliGroup(len(short_address_list), self.numberofgroups, short_address_list)
		self.numberofgroups = self.numberofgroups + 1
		return self.numberofgroups

	def addtoDALIGroup(self, GroupNumber, short_address):
		"""
		Add singular luminaire to group
		:param GroupNumber: Group to update
		:param short_address: Short address of luminaire
		:return:
		"""

		"""
		Follows format:
		
		YAAAAAA1 0110XXXX
		Where Y is selector bit  0  is direct arc power - 1 is command following 
		AAAAAA is short address
		XXXX is Group number
		
		1000 0001 = 129
		000 000 is replaced with short address << 1 bit
		"""
		topByte = (129 + (short_address << 1))
		topByte = '{0:0{1}X}'.format(topByte, 2)
		"""
		0110 XXXX = 96
		where XXXX is Group Number 
		"""
		lowByte = 96 + GroupNumber
		lowByte = '{0:0{1}X}'.format(lowByte, 2)

		self.daliSerialCommand.dali_send_16_twice_cmd(topByte, lowByte, False)

		self.groups[GroupNumber].add_member(short_address)

	def removefromDALIGroup(self, GroupNumber, short_address):
		"""
		Removes luminaire from Group
		:param GroupNumber: Group to update 1-16
		:param short_address: Short address of luminaire
		:return: None
		"""
		"""
		Follows format:

		YAAAAAA1 0110XXXX
		Where Y is selector bit  0  is direct arc power - 1 is command following 
		AAAAAA is short address
		XXXX is Group number

		1000 0001 = 129
		000 000 is replaced with short address << 1 bit
		"""
		topByte = (129 + (short_address << 1))
		topByte = '{0:0{1}X}'.format(topByte, 2)
		"""
		0111 XXXX = 112
		where XXXX is Group Number 
		"""
		lowByte = 112 + GroupNumber
		lowByte = '{0:0{1}X}'.format(lowByte, 2)

		self.daliSerialCommand.dali_send_16_twice_cmd(topByte, lowByte, False)

		self.groups[GroupNumber].remove_member(short_address)

	def findDALIGroups(self):
		"""
		Finds DALI Groups with members
		"""
		for i in range(len(self.groups)):
			if self.groups[i].numMembers != 0:
				print("Group " + str(self.groups[i].groupNum)+ ": has "+ str(self.groups[i].numMembers)+ " members")

	def fetchDALIGroups(self):
		"""
		fetches all dali groups from the bus
		"""
		for i in range(len(self.groups)):
			self.fetchDALIGroup(i)

	def fetchDALIGroup(self, GroupNumber):

		lowbyte = '91'
		hasMembers = False
		groupstosearch = []
		self.daliSerialCommand.dali_send_16_cmd('%02x' % (GroupNumber * 2 + 129), lowbyte, False)
		rsp = self.daliSerialCommand.dali_read_bytes()
		if rsp[0] == 'J' or rsp[0] == 'D' or rsp[0] == 'X':
			print('Multiple member(s) in group %2d' % GroupNumber)
			hasMembers = True
		time.sleep(.03)

		if hasMembers:
			self.searchGroupMembers(GroupNumber)

	def searchGroupMembers(self, GroupNumber):
		short_addr = 0
		lowbyte = "C0"
		bit = 1 << (GroupNumber & 7)
		if GroupNumber > 7:
			lowbyte = "C1"
		found = 0
		members = []
		while short_addr < 64:
			self.daliSerialCommand.dali_send_16_cmd('%02x' % (short_addr * 2 + 1), lowbyte, False)
			rsp = self.daliSerialCommand.dali_read_bytes()
			if rsp[0] == 'D':
				print('DALI Power Issue')
			if rsp[0] == 'J':
				text = rsp[1:3]
				response = int(text, 16)
				if response & bit:
					print('Address %d is a member' % short_addr)
					found = 1
					members.append(short_addr)

			self.daliSerialCommand.dali_read_bytes()
			short_addr = short_addr + 1
			time.sleep(.02)
		if found == 1:
			self.groups[GroupNumber].set_members(members)
		if found == 0:
			print(' no members ')

	def controlgroup(self, GroupNumber, PowerLevel):


		#Send group direct control command

		if PowerLevel >= 0 and PowerLevel < 256 and GroupNumber >= 0 and GroupNumber < 16:
			highbyte = (GroupNumber << 1) + 128
			highbyte = '{0:0{1}X}'.format(highbyte, 2)
			lowbyte = '{0:0{1}X}'.format(PowerLevel, 2)

			self.daliSerialCommand.dali_send_16_cmd(highbyte,lowbyte, False)
			self.daliSerialCommand.dali_read_bytes()

	def directcontrol_individual(self, ShortAddr, PowerLevel):

		# Send direct addr control

		if PowerLevel >= 0 and PowerLevel < 256 and ShortAddr >= 0 and ShortAddr < 64:

			highbyte = (ShortAddr << 1)
			highbyte = '{0:0{1}X}'.format(highbyte, 2)
			lowbyte = '{0:0{1}X}'.format(PowerLevel, 2)

			self.daliSerialCommand.dali_send_16_cmd(highbyte,lowbyte, False)
