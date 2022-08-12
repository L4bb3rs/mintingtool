import requests
import urllib3
import json
import time
from os import path
from logging import getLogger,\
    basicConfig,\
    INFO, DEBUG, WARNING, ERROR, CRITICAL,\
    Formatter,\
    StreamHandler, FileHandler
urllib3.disable_warnings()

json_data = '{}'
wallet_RPC_port = 'localhost:9256'
homeDir = path.expanduser('~')
cert = (homeDir+'/.chia/mainnet/config/ssl/wallet/private_wallet.crt', homeDir+'/.chia/mainnet/config/ssl/wallet/private_wallet.key')


working_folder_path: str = path.join(path.expanduser("~"), 'mintingtool')
coin_denominator: int = 1000000000000

class WalletAPIwrapper():
    def __init__(self):
        self._log = getLogger()

    def query_wallet(self,
                    url_option,
                    json_data):
        try:
            return requests.post(url='https://{}/{}'.format(wallet_RPC_port, url_option),
                                    verify=False,
                                    cert=cert,
                                    headers = {'content-type': 'application/json'},
                                    json=json_data,
                                    ).json()
        except:
            self._log.error('Error found while querying the wallet, {} with json {}:\n'.format(url_option,
                                                                                                 json_data))
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
                                                        datetime.now() == self.exec_starttime) + ' ' + self.additional_msg)

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

def get_fingerprints(): #returns all fingerprints from the chia instance
    url_option = "get_public_keys"
    public_keys = ''
    response = WalletAPIwrapper().query_wallet(url_option=url_option, json_data=json_data)
    public_keys = response['public_key_fingerprints']
    return public_keys

def get_fingerprint(): #returns the currently signed in fingerprint
    url_option = "get_logged_in_fingerprint"
    response = WalletAPIwrapper().query_wallet(url_option=url_option, json_data=json_data)
    fingerprint = response['fingerprint']
    return fingerprint

def login_chia(fingerprint): #log in via RPC, to be used for future functionality
    data = '{{}}'.format(fingerprint)
    url_option = "log_in"
    response = WalletAPIwrapper().query_wallet(url_option=url_option, json_data=data)
    return data

def list_nfts(): #lists all NFTs from the default nft wallet, need to expand to iterate through all NFT wallets. added for future functionality
    nft_list = ''
    url_option = "nft_get_nfts"
    json_data = json.loads(nft_wallet_data)
    response = WalletAPIwrapper().query_wallet(url_option=url_option, json_data=json_data)
    for nft in range(len(response['nft_list'])):
        nft_list = nft_list + response['nft_list'][nft]['launcher_id'] + '\n'
    return nft_list

def list_nft_wallets(): #lists the id of all NFT wallets that have associated dids
    nft_wallet_list = []
    url_option = "nft_get_wallets_with_dids"
    response = WalletAPIwrapper().query_wallet(url_option=url_option, json_data=json_data)
    if len(response['nft_wallets']) > 1:
        for wallet in response['nft_wallets']:
            nft_wallet_list.append(wallet['wallet_id'])
    else:
        nft_wallet_list = response['nft_wallets'][0]['wallet_id']
    return nft_wallet_list

def list_dids(did_wallet_data): #to-do link this call to GUI.py to pull DID for selected wallet (one method of doing so, other method is extracting DID information from nft wallet command above)
    did_list = ''
    url_option = "did_get_did"
    json_data = json.loads(did_wallet_data)
    return WalletAPIwrapper().query_wallet(url_option=url_option, json_data=json_data)

def list_wallets(): #lists all wallets with id, type, and name
    wallet_list = ''
    url_option = "get_wallets"
    response = WalletAPIwrapper().query_wallet(url_option=url_option, json_data=json_data)
    for wallet in range(len(response['wallets'])):
        wallet_list = wallet_list + 'wallet_id: ' + str(response['wallets'][wallet]['id']) + ', wallet_type: ' + str(response['wallets'][wallet]['type']) + ', wallet_name: ' + str(response['wallets'][wallet]['name'])
    return wallet_list

def get_network(): #network prefix field has been added for future functionality
    network_name = ''
    network_prefix = ''
    url_option = "get_network_info"
    response = WalletAPIwrapper().query_wallet(url_option=url_option, json_data=json_data)
    if response != None:
        network_name = response['network_name']
        network_prefix = response['network_prefix']
    else:
        print('The wallet RPC cannot be reached to verify network information, make sure Chia is running')
        network_name = 'unknown'
        network_prefix = 'unknown'
    return network_name

def get_sync():
    sync_status = ''
    url_option = "get_sync_status"
    response = WalletAPIwrapper().query_wallet(url_option=url_option, json_data=json_data)
    if response != None:
        if response['synced'] == False:
            if response['syncing'] == True:
                sync_status = 'Syncing'
            else: sync_status = 'Not Synced'
        else: sync_status = 'Synced'
    else:
        print('The wallet RPC cannot be reached to verify sync status, make sure Chia is running')
        sync_status = 'Not Synced'
    return sync_status

def nft_mint_nft(url, data): 
    sync_status = ''
    url_option = "nft_mint_nft"
    response = json.loads(requests.post(url, data=data, headers=headers, cert=cert, verify=False).text)
    return response


def main():
    if get_sync() == 'Not Synced':
        print('The chia client is: ' + get_sync())
    else:
        while get_sync() == 'Syncing':
            fingerprint = get_fingerprint()
            print('The chia client is: ' + get_sync())
            print('The signed in fingerprint: ' + str(fingerprint))
            print('Sleeping for five seconds while the chia client syncs')
            time.sleep(5)
        if get_sync() == 'Synced':
            fingerprint = get_fingerprint()
            nft_wallets = list_nft_wallets()
            did_wallet_data = '{"wallet_id": 4}'
            did = list_dids(did_wallet_data)
            print('The chia client is: ' + get_sync())
            print('The signed in fingerprint: ' + str(fingerprint))
            #print(list_nfts())
            print('Contains the following NFT Wallet IDs that have associated DIDs: ' + str(nft_wallets))
            print('DID: ' + str(did))
            #print(list_dids())
main()
