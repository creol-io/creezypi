#
#
#  _   _ ______ _______ ____   __  __          _   _
# | \ | |  ____|__   __/ __ \ / _|/ _|        | | | |
# |  \| | |__     | | | |  | | |_| |_ ___  ___| |_| |_ ___ _ __
# | . ` |  __|    | | | |  | |  _|  _/ __|/ _ \ __| __/ _ \ '__|
# | |\  | |       | | | |__| | | | | \__ \  __/ |_| ||  __/ |
# |_| \_|_|       |_|  \____/|_| |_| |___/\___|\__|\__\___|_|
#
#
#
# Author: Joshua Bijak
# Date:  29/01/2020
# Desc:  Module to handle burning of offsets from this specific Pi to NFT subtokens owned by the user
# Changelog: 29/01/2020 - First Write
#


class NTFOffsetter:
    CarbonNFTAddresses = []

    def __init__(self, CarbonNFTs_):
        """
        Initializes Carbon NFT class
        :param CarbonNFTs_:
        """
        self.CarbonNFTAddresses = CarbonNFTs_

    def set_NFT_address(self, CarbonNFTs_):
        """
        Sets the NFT Smart contract address for this set of carbon credits
        :param CarbonNFTs_: ethereum address in hex string
        :type CarbonNFTs_: string array
        """

    def approve_Burn(self, CarbonNFTs_):
        """
        Ask each NFT Subtoken for required burn approval
        :return:
        """

    def start_offset(self):
        """
        Starts the offset process in the smart contracts
        :return:
        :rtype:
        """

        
    def finish_offset(self):
        """
        Finishes the offsetting process after the GridMix contract returns
        :return:
        :rtype:
        """