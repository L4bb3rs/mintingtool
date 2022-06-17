import subprocess
import sys
import PySimpleGUI as sg
from pathlib import Path
from typing import Tuple, List, Optional

import cdv.clibs as std_lib
from blspy import G1Element
from cdv.util.load_clvm import load_clvm
from clvm.casts import int_from_bytes

from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_spend import CoinSpend
from chia.util.ints import uint64
from chia.rpc import (
    full_node_rpc_api,
    wallet_rpc_api,
)

sg.theme('BluePurple')


def main():
    layout = [  [sg.Text('Enter a command to execute (e.g. dir or ls)'),
            sg.Text('Enter the fingerprint to be used')],
            [sg.Input(key='_IN_'),
            sg.Button('Run'),
            sg.Input(key='_FINGERPRINT_')],             # input field where you'll type command
            [sg.Output(size=(120,45))],          # an output area where all print output will go
            [sg.Button('startChia'),
            sg.Button('getFingerprint'),
            sg.Button('getPublic'),
            sg.Button('createWallet'),
            sg.Button('walletStatus'),
            sg.Button('mintNFT'),
            sg.Button('infoNFT'),
            sg.Button('stopChia'),
            sg.Button('Exit')] ]     # a couple of buttons

    window = sg.Window('NFT Minting Tool', layout)
    while True:             # Event Loop
        event, values = window.Read()
        if event in (None, 'Exit'):         # checks if user wants to
            exit
            break

        if event == 'Run':
            runCommand(cmd=values['_IN_'], window=window)

        if event == 'startChia':
            startChia = "chia start wallet"
            runCommand(cmd=startChia, window=window)

        if event == 'getFingerprint':
            getFingerprint = "chia rpc wallet get_logged_in_fingerprint"
            runCommand(cmd=getFingerprint, window=window)

        if event == 'getPublic':
            getPublic = "chia rpc wallet get_public_keys"
            runCommand(cmd=getPublic, window=window)


        if event == 'createWallet':
            createWallet = "chia rpc wallet create_new_wallet -j wallet.json"
            runCommand(cmd=createWallet, window=window)

        if event == 'walletStatus':                  # the two lines of code needed to get button and run command
            walletStatus = "chia wallet show -f "+values['_FINGERPRINT_']
            runCommand(cmd=walletStatus, window=window)

        if event == 'mintNFT':
            mintNFT = "chia rpc wallet nft_mint_nft -j data.json"
            runCommand(cmd=mintNFT, window=window)

        if event == 'infoNFT':
            infoNFT = "chia rpc wallet nft_get_nfts -j walletID.json"
            runCommand(cmd=infoNFT, window=window)

        if event == 'stopChia':
            stopChia = "chia stop all"
            runCommand(cmd=stopChia, window=window)

    window.Close()

# This function does the actual "running" of the command.  Also watches for any output. If found output is printed
def runCommand(cmd, timeout=20, window=None):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    output = ''
    for line in p.stdout:
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
        output += line
        print(line)
        window.Refresh() if window else None        # yes, a 1-line if, so shoot me
    retval = p.wait(timeout)
    print("________________________________________________________________")
    print("____________________END_OF_COMMAND______________________________")
    print("________________________________________________________________")
    return (retval, output)                         # also return the output just for fun

if __name__ == '__main__':
    main()
