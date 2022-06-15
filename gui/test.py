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
    layout = [  [sg.Text('Enter a command to execute (e.g. dir or ls)')],
            [sg.Input(key='_IN_')],             # input field where you'll type command
            [sg.Output(size=(120,15))],          # an output area where all print output will go
            [sg.Button('walletStatus'), sg.Button('Run'), sg.Button('Exit')] ]     # a couple of buttons

    window = sg.Window('NFT Minting Tool', layout)
    while True:             # Event Loop
        event, values = window.Read()
        if event in (None, 'Exit'):         # checks if user wants to
            exit
            break

        if event == 'walletStatus':                  # the two lines of code needed to get button and run command
            walletStatus = "chia wallet show -f 1714468734"
            runCommand(cmd=walletStatus, window=window)

    window.Close()

# This function does the actual "running" of the command.  Also watches for any output. If found output is printed
def runCommand(cmd, timeout=20, window=None):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    output = ''
    for line in p.stdout:
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
        output += line
        print(line)
        window.Refresh() if window else None        # yes, a 1-line if, so shoot me
    retval = p.wait(timeout)
    print("________________________________________________________________")
    return (retval, output)                         # also return the output just for fun


if __name__ == '__main__':
    main()
