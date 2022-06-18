  # essential for functions
import subprocess
import os.path
import sys
import PySimpleGUI as sg
from logging import getLogger,\
    basicConfig,\
    INFO, DEBUG, WARNING, ERROR, CRITICAL,\
    Formatter,\
    StreamHandler, FileHandler
from pathlib import Path
from typing import Tuple, List, Optional

  # cryptography and clvm
import cdv.clibs as std_lib
from blspy import G1Element
from cdv.util.load_clvm import load_clvm
from clvm.casts import int_from_bytes

  # clsp
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_spend import CoinSpend
from chia.util.ints import uint64

  # rpc
import rpyc
from chia.rpc import (
    full_node_rpc_client,
    wallet_rpc_client,
    rpc_client,
)

  # assets
conn = rpyc.classic.connect("localhost:9256")
working_folder_path: str = path.join(path.expanduser("~"), 'mintingtool')
wallet_RPC_port: int = 9256
coin_denominator: int = 1000000000000

class WalletAPIwrapper():
    def __init__(self):
        self._log = getLogger()

    def query_wallet(self,
                    url_option,
                    json_data):
        try:
            return requests.post(url='https://localhost:{wallet_RPC_port}\{url_option}'.format(wallet_RPC_port=wallet_RPC_port,
                                                                                                url_option=url_option),
                                    verify=False,
                                    cert=(r'{}/.chia/mainnet/config/ssl/wallet/private_wallet.crt'.format(path.expanduser("~")),
                                          r'{}/.chia/mainnet/config/ssl/wallet/private_wallet.crt'.format(path.expanduser("~"))),
                                    headers = {'content-type': 'application/json'},
                                    json=json_data,
                                    ).json()
        except:
            self._log.error('Error found while querying the wallet, {} with json {}:\n{}'.format(url_option,
                                                                                                 json_data,
                                                                                                 format_exc(chain=False)))
            return None
class ContextBase():

    _log: getLogger() = None

    def __init__(self):
        super(ContextBase, self),__init__()
        self.additional_msg = ''

    def __enter__(self):
        self.exec_starttime = datetime.now()

        if not self._log:
            self._log = gotLogger()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._log.info('Execution of {} took {}'.format(type(self).__name__,
                                                        datetime.now() = self.exec_starttime) + ' ' + self.additional_msg)

class json_ops_class():

    _log: getLogger = None

    def __init__(self):
        if not self._lof:
            self._log = getLogger()
        if not path.isdir('wd'):
            mkdir('wd')
            self._log.debug('The working dir was created.')

        super(json_ops_class, self).__init__()

    def read_json(self,
                  json_filepath):
        while True:
            try:
                with open(json_filepath, 'r') as json_in_handle:
                    return load(json_in_handle)
            except:
                self._log.warning('Retrying load of {}, failed because \n{}'.format(json_filepath,
                                                                        format_exc(chain=False)))
            sleep(1)

    def save_json(self,
                  json_filepath,
                  obj):
        while True:
            try:
                if not path.isdir(os.path.dirname(json_filepath)):
                    mkdir(os.path.dirname(json_filepath))

                with open(json_filepath, 'w') as json_out_handle:
                    return dump(obj, json_out_handle, indent=2)
            except:
                self._log.warning('Retrying dump in {}, failed because \n{}'.format(json_filepath,
                                                                        format_exc(chain=Failse)))
            sleep(1)

def configure_logger():
    class CustomFormatter(Formatter):
        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format = '%(asctime)s,%(msecs)d %(levelname)-4s [%(filename)s:%(lineo)d -> %(name)s - %(funcName)s] __ %(message)s'

        FORMATS = {
            DEBUG: grey + format + reset,
            INFO: grey + format + reset,
            WARNING: yellow + format + reset,
            ERROR: red + format + reset,
            CRITICAL: bold_red + format + reset,
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = Formatter(log_fmt)
            return formatter.format(record)

    ch = StreamHandler(stream=stdout)
    ch.setLevel(DEBUG)
    ch.setFormatter(CustomFormatter())
    fh = FileHandler("runtime_log.log")
    fh.setLevel(DEBUG)
    fh.setFormatter(Formatter('%(asctime)s,%(msecs)d %(levelname)-4s [%(filename)s:%(lineo)d -> %(name)s - %(funcName)s] __ %(message)s'))

    basicConfig(datefmt='%Y-%m-%d:%H:%M:%S'
                level=INFO,
                handlers=[fh,ch])


layout = [  [sg.Text('Enter a command to execute (e.g. dir or ls)'),
        sg.Text('Enter the fingerprint to be used')],
        [sg.Input(key='_IN_'),
        sg.Button('Run'),
        sg.Input(key='_FINGERPRINT_')],             # input field where you'll type command
        [sg.Output(size=(120,50))],          # an output area where all print output will go
        [sg.Button('initChia'),
        sg.Button('generateKey'),
        sg.Button('startChia'),
        sg.Button('showKeys'),
        sg.Button('getFingerprint'),
        sg.Button('getPublic'),
        sg.Button('createWallet'),
        sg.Button('walletStatus'),
        sg.Button('mintNFT'),
        sg.Button('infoNFT'),
        sg.Button('stopChia'),
        sg.Button('Exit')] ]     # a couple of buttons

sg.theme('BluePurple')


def main():
    window = sg.Window('NFT Minting Tool', layout)
    while True:             # Event Loop
        event, values = window.Read()
        if event in (None, 'Exit'):         # checks if user wants to
            exit
            break

        if event == 'Run':
            runCommand(cmd=values['_IN_'], window=window)

        if event == 'initChia':
            startChia = "chia init"
            runCommand(cmd=initChia, window=window)

        if event == 'generateKey':
            startChia = "chia keys generate"
            runCommand(cmd=generateKey, window=window)

        if event == 'startChia':
            startChia = "chia start wallet"
            runCommand(cmd=startChia, window=window)

        if event == 'showKeys':
            startChia = "chia keys show"
            runCommand(cmd=showKeys, window=window)

        if event == 'getFingerprint':
            getFingerprint = "chia rpc wallet get_logged_in_fingerprint"
            runCommand(cmd=getFingerprint, window=window)

        if event == 'getPublic':
            getPublic = "get_public_keys"
            runRPC(cmd=getPublic, window=window)


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

def runRPC(self, timeout=20, window=None):
    conn.execute('get_public_keys')
    print("________________________________________________________________")
    print("____________________END_OF_COMMAND______________________________")
    print("________________________________________________________________")

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
