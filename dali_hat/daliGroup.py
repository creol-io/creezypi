
#      _       _ _  _____
#     | |     | (_)/ ____|
#   __| | __ _| |_| |  __ _ __ ___  _   _ _ __
#  / _` |/ _` | | | | |_ | '__/ _ \| | | | '_ \
# | (_| | (_| | | | |__| | | | (_) | |_| | |_) |
#  \__,_|\__,_|_|_|\_____|_|  \___/ \__,_| .__/
#                                        | |
#                                        |_|


# Author: Joshua Bijak
# Date:  29/01/2020
# Desc:  Class to hold DALI groups as objects
# Changelog: 29/01/2020 - First Write
#


class daliGroup:
    numMembers = 0
    groupNum = 0
    members = []

    def __init__(self, numMembers_, groupNum_, members_):
        self.numMembers = numMembers_
        self.groupNum = groupNum_
        self.members = members_

    def get_group_num(self):
        return self.groupNum

    def get_num_members(self):
        return self.numMembers

    def set_group_num(self, groupNum_):
        self.groupNum = groupNum_

    def set_num_members(self, numMembers_):
        self.numMembers = numMembers_

    def get_members(self):
        return self.members

    def set_members(self, members_):
        self.members = members_
        self.numMembers = len(members_)

    def remove_member(self, member_to_remove):
        if member_to_remove in self.members:
            self.members.remove(member_to_remove)
        self.numMembers = self.numMembers-1

    def add_member(self, member_to_add):
        if member_to_add not in self.members:
            self.members.append(member_to_add)
        self.numMembers = self.numMembers + 1
