import requests
import urllib3
import json
import os
urllib3.disable_warnings()

data = '{}'
url = "https://localhost:9256/"
homeDir = os.path.expanduser('~')
headers = {'Content-Type': 'application/json'}
nft_wallet_data = '{"wallet_id":83}'
did_wallet_data = '{"wallet_id":82}'
cert = (homeDir+'/.chia/mainnet/config/ssl/wallet/private_wallet.crt', homeDir+'/.chia/mainnet/config/ssl/wallet/private_wallet.key')

def get_fingerprint(url): #returns the currently signed in fingerprint
    command = "get_logged_in_fingerprint"
    url = url+command
    response = json.loads(requests.post(url, data=data, headers=headers, cert=cert, verify=False).text)
    fingerprint = response['fingerprint']
    return fingerprint

def list_nfts(url): #lists all NFTs from the default nft wallet, need to expand to iterate through all NFT wallets
    nft_list = ''
    command = "nft_get_nfts"
    url = url+command
    data = nft_wallet_data
    response = json.loads(requests.post(url, data=data, headers=headers, cert=cert, verify=False).text)
    for nft in range(len(response['nft_list'])):
        nft_list = nft_list + response['nft_list'][nft]['nft_coin_id'] + '\n'
    return nft_list

def list_nft_wallets(url): #lists the id of all NFT wallets that have associated dids
    nft_wallet_list = ''
    command = "nft_get_wallets_with_dids"
    url = url+command
    response = json.loads(requests.post(url, data=data, headers=headers, cert=cert, verify=False).text)
    for wallet in range(len(response['nft_wallets'])):
        nft_wallet_list = nft_wallet_list + str(response['nft_wallets'][wallet]['wallet_id']) + '\n'
    return nft_wallet_list

def list_dids(url): #currently lists did from default did wallet, need to expand to iterate through did wallets
    did_list = ''
    command = "did_get_did"
    url = url+command
    data = did_wallet_data
    response = json.loads(requests.post(url, data=data, headers=headers, cert=cert, verify=False).text)
    did_list = response['my_did']
    return did_list

def list_wallets(url): #lists all wallets with id, type, and name
    wallet_list = ''
    command = "get_wallets"
    url = url+command
    response = json.loads(requests.post(url, data=data, headers=headers, cert=cert, verify=False).text)
    for wallet in range(len(response['wallets'])):
        wallet_list = wallet_list + 'wallet_id: ' + str(response['wallets'][wallet]['id']) + ', wallet_type: ' + str(response['wallets'][wallet]['type']) + ', wallet_name: ' + str(response['wallets'][wallet]['name']) + '\n'
    return wallet_list


print('-------')
print('Fingerprint logged in: ' + '\n' + str(get_fingerprint(url)))
print('-------')
#print('List of owned NFTs: ' + '\n' + str(list_nfts(url)))
print('-------')
print('List of NFT wallet ids: ' + '\n' + str(list_nft_wallets(url))) 
print('-------')
print('List of DIDs: ' + '\n' + str(list_dids(url)))
print('-------')
#print('List of Wallets: ' + '\n' + str(list_wallets(url)))
print('-------')
print('I will use wallet ID: ' + str(list_nft_wallets(url)) + ' and did: ' + str(did_list) + ' to mint an NFT')
