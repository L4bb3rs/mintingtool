import yaml
import PySimpleGUI as sg
from sha256_hash import sha256Checksum as FileHash
import rpc_client
#from PIL import Image
import requests
from io import BytesIO
import json
from json import (load as jsonload, dump as jsondump)
# import threading
# import time
# import sys
import config
from os import path

# constants
nft_wallet_id = '-NFT WALLET ID-'
wallet_address = '-WALLET ADDRESS-'
theme = '-THEME-'
########################################## Define Defaults ##########################################
# to-do add validation of selected network, if not selected network break and instruct user to change network via cli
NETWORK_NAME = 'testnet10'

CUSTOM_ICON = path.join(path.dirname(__file__), r'NFTr.ico')

# to-do add functionality of right click menu
right_click_menu = ['Unused', ['Cut', 'Copy', 'Paste', 'About']]

loadingGIF = config.LOADING_GIF  # to-do add loading screen in thread

THREAD_EVENT = '-THREAD-'
SETTINGS_FILE = path.join(path.dirname(__file__), r'settings_file.cfg')
DEFAULT_SETTINGS = {'fingerprint': 0xdeadbeef,
                    'nft_wallet_id': None, 'wallet_address': None, 'theme': sg.theme()}
# "Map" from the settings dictionary keys to the window's element keys
# DID to be added once wallet creation is added
SETTINGS_KEYS_TO_ELEMENT_KEYS = {'nft_wallet_id': nft_wallet_id,
                                 'wallet_address': wallet_address, 'theme': theme}

nft_data = {"wallet_id": 3,   # 3 is default as this should be the NFT wallet if no additional wallets have been created
            "uris": [""],
            "hash": "",
            "meta_uris": [""],
            "meta_hash": "",
            "license_uris": [""],
            "license_hash": "",
            "royalty_address": "",
            "royalty_percentage": 5,  # 5 is the default
            "target_address": "",
            "edition_number": 1,  # 1/1 editions are default
            "edition_count": 1,  # 1/1 editions are default
            "did_id": None,  # No initial DID owner is the default
            "fee": 615000000}  # min recommended minting fee is deafult

########################################## Define Text Sizes ##########################################
inputsize = (25, 3)
textsize1 = (5, 1)
textsize2 = (10, 1)
textsize3 = (22, 1)
textsize4 = (80, 1)

########################################## Define Text Boxes and Popups ##########################################


def text_label1(text): return sg.Text(
    text+':', justification='r', size=(15, 1))
def text_label2(text): return sg.Text(
    text+':', justification='l', size=(11, 1))


def text_label3(text): return sg.Text(text+':', justification='l', size=(3, 1))
def text_label4(text): return sg.Text(text+':', justification='l', size=(5, 1))
def text_label5(text): return sg.Text(
    text+':', justification='l', size=(12, 1))


def text_label6(text): return sg.Text(text+':', justification='l', size=(8, 1))


def output_text1(text): return sg.InputText(text, use_readonly_for_disable=True, disabled=True,
                                            disabled_readonly_background_color=sg.theme_text_element_background_color())


def output_text2(text, key): return sg.InputText(text, key=key, use_readonly_for_disable=True,
                                                 disabled=True, disabled_readonly_background_color=sg.theme_text_element_background_color())


def output_text3(text, key, tooltip): return sg.InputText(text, key=key, size=textsize2, tooltip=tooltip,
                                                          use_readonly_for_disable=True, disabled=True, disabled_readonly_background_color=sg.theme_text_element_background_color())


def header_text1(key, tooltip): return sg.Text(
    key=key, size=(5, 1), tooltip=tooltip)  # wallet ID


def header_text2(key, tooltip): return sg.Text(
    key=key, size=(12, 1), tooltip=tooltip)  # Theme


def header_text3(key, tooltip): return sg.Text(
    key=key, size=(35, 1), tooltip=tooltip)  # Wallet Address


def header_text4(text, tooltip): return sg.Text(
    text=text, size=(10, 1), tooltip=tooltip)  # Fingerprint


def header_text5(text, tooltip): return sg.Text(
    text=text, size=(57, 1), tooltip=tooltip)  # DID


def input_text1(key, tooltip): return sg.Input(
    key=key, size=textsize1, tooltip=tooltip)


def input_text2(key, tooltip): return sg.Input(
    key=key, size=textsize2, tooltip=tooltip)


def input_text3(key, tooltip): return sg.Input(
    key=key, size=textsize3, tooltip=tooltip)


def input_text4(key, tooltip): return sg.Input(
    key=key, size=textsize4, tooltip=tooltip)


def input_text5(text, key, tooltip): return sg.Input(
    text, key=key, size=textsize2, tooltip=tooltip)


def coming_soon(title, text, tooltip): return sg.Frame(
    title, [[sg.Text(text, size=textsize2, tooltip=tooltip)]])


def pop_up(message, title, notitle): return sg.popup(
    message, title=title, no_titlebar=notitle, keep_on_top=True)


def popup_quick(message): return sg.popup_quick_message(
    message, keep_on_top=True, background_color='red', text_color='white', no_titlebar=True)


def load_settings(settings_file, default_settings):
    '''Load/Save Settings File'''
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
    except Exception as e:
        settings = ''
        popup_quick(
            f'exception {e}, No settings file found... will create one for you')
        settings = default_settings
        save_settings(settings_file, settings, None)
        event, values = create_settings_window(settings).read(close=True)
        if event == 'Save':
            save_settings(SETTINGS_FILE, settings, values)
        elif event in (sg.WIN_CLOSED, 'Exit'):
            print('Settings window closed without saving', '', True)
    return settings


def refresh_settings(settings, window):
    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(
                value=settings[key])
        except Exception:
            print(
                f'Problem updating PySimpleGUI window from settings. Key = {key}')


def save_settings(settings_file, settings, values):
    """If there are stuff specified by another window, fill in those values
        update window with the values read from settings file"""
    if values:
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception:
                print(
                    f'Problem updating settings from window values. Key = {key}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)

    sg.popup('Settings saved')


def wallet_popup():  # defines Wallet IDs popup window
    '''Wallet IDs p'''
    message = rpc_client.list_wallets()
    layout = [[sg.Multiline(message, size=(90, 35))]]
    sg.Window('NFT Wallet List', layout, keep_on_top=True,
              finalize=True, icon=CUSTOM_ICON)


def create_settings_window(settings):
    '''Make a settings window'''
    sg.theme(settings['theme'])
    # adjust nft wallet list to be displayed properly
    if type(rpc_client.list_nft_wallets()) == int:
        nft_wallet_list = json.dumps(rpc_client.list_nft_wallets())
    else:
        nft_wallet_list = rpc_client.list_nft_wallets()
    nft_wallet_did = rpc_client.nft_get_wallet_did(settings['nft_wallet_id'])

    layout = [[sg.Text('Settings', font='Any 15')],  # to-do update initial settings to default on logged in fingerprint, pull first NFT wallet ID with associated DID, and display that DID. readd these to settings file so defaults can be stored
              [text_label1('Fingerprint'), output_text1(
                  rpc_client.get_fingerprint())],
              [text_label1('NFT Wallet ID'), sg.Combo(
                  nft_wallet_list, size=(20, 20), key=nft_wallet_id)],
              [text_label1('Wallet Address'), sg.Input(
                  rpc_client.get_address(), key=wallet_address)],
              [text_label1('DID'), output_text1(nft_wallet_did)],
              [text_label1('Theme'), sg.Combo(
                  sg.theme_list(), size=(20, 20), key=theme)],
              [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Settings', layout, keep_on_top=True,
                       finalize=True, icon=CUSTOM_ICON)

    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(
                value=settings[key])
        except Exception:
            print(
                'Problem updating PySimpleGUI window from settings. Key = {key}', '', True)

    return window


def file_hash(list):
    """Define File Hashing"""
    fhash = ''
    u = 0
    hash_list = []
    print('hashing url list: {} with length: {}'.format(list, len(list)))
    while u < len(list):
        print('attempting hash for {}'.format(list[u]))
        fhash = FileHash(None, str(list[u]))
        hash_list.append(fhash)
        print('hash list: {}'.format(hash_list))
        if u > 0:  # separate into own function and iterate though full hash list at once
            if hash_list[u] == hash_list[0]:
                print('################# HASH CONFIRMED ###################')
                print('hash #{} matches the first url file hash'.format(u+1))
                hash_verify = hash_list[0]
                print('################# END CONFIRMED HASH ###############')
            else:
                print('################### HASH FAILED #####################')
                print('hash #{} does not match the first url file hash\n'.format(u+1))
                print('first file hash: {}'.format(hash_list[0]))
                print('mismatched file hash: {}'.format(hash_list[u]))
                hash_verify = 'hash #{} does not match the first url file hash'.format(
                    u+1)
                print('################### END FAILED HASH #################')
        else:
            hash_verify = hash_list[0]
        u += 1
    return hash_verify


def hashing(values):
    try:
        # Verifies URLs are entered for each field, to-do iterate over list of fields
        nlist = url_split(values['_U_'])
        filehash = file_hash(nlist)
    except Exception:
        print('error deriving file hash, please verify url(s)')
        filehash = 'error'
    try:
        nlist = url_split(values['_MU_'])
        metahash = file_hash(nlist)
    except Exception:
        print('error deriving metafile hash, please verify url(s)')
        metahash = 'error'
    try:
        nlist = url_split(values['_LU_'])
        licensehash = file_hash(nlist)
    except Exception:
        print('error deriving license hash, please verify url(s)')
        licensehash = 'error'
    return filehash, metahash, licensehash


def url_split(url):
    """splits urls prio to file hashing if multiple are present and separated with commas"""
    try:
        print('attempting url split for {}'.format(url))
        nlist = url.replace(" ", "")
        # to-do add handling for blank entries after comma
        nlist = [list.split(',')]
        nlist = [0]
        print(len(nlist))
        print(type(nlist))
    except Exception:
        print('URL split failed')
        nlist = url
    return nlist

########################################## Define Page Refresh ##########################################


def refresh(settings, window, values):
    print(values)
    print(rpc_client.get_sync())
    message, filehash, metahash, licensehash = page_refresh(
        settings, window, values)
    window['-OUTPUT-'].update(message)   # updates preview window
    return filehash, metahash, licensehash


def page_refresh(settings, window, values):
    message = ''
    print('running refresh')
    refresh_settings(settings, window)
    filehash, metahash, licensehash = hashing(
        values)  # to-do add image display to preview
    rp = int(values['_RP_']) / 100
    message = "Edition: {} out of {} \n \n File URL: {} \n \n File Hash: {} \n \n MetaData URL: {} \n \n MetaData Hash: {} \n \n License URL: {} \n \n License Hash: {} \n \n Royalty Percentage: {}% \n \n Minting Fees: 65,000,001 Mojo".format(
        values['_EN_'], values['_EC_'], values['_U_'], filehash, values['_MU_'], metahash, values['_LU_'], licensehash, rp)
    return message, filehash, metahash, licensehash


def loading():
    """Loading GIF"""
    for _ in range(5):
        sg.PopupAnimated(loadingGIF, background_color='white',
                         time_between_frames=100)
    sg.PopupAnimated(None)

########################################## Define Threading ##########################################


def monitor_window(status, note):
    if status == False:
        state = 'Minting in Progress'
    elif status == True:
        state = 'Minted Successfully'
    mintstatus = [[sg.Text('Minting Status:', justification='r', size=(15, 1)), sg.InputText(state, key='-STATUS-', use_readonly_for_disable=True, disabled=True, disabled_readonly_background_color=sg.theme_text_element_background_color())],
                  [sg.Text('Elapsed Time:', justification='r', size=(15, 1)), sg.InputText(note, key='-TIME-', use_readonly_for_disable=True, disabled=True, disabled_readonly_background_color=sg.theme_text_element_background_color())]]
    columnmint = [[sg.Frame('', layout=mintstatus, border_width=10)]]
    window = sg.Window('', columnmint, size=(425, 125), keep_on_top=True,
                       finalize=True, icon=CUSTOM_ICON, auto_close=True, auto_close_duration=5)

    window.read()


def mint_monitor():
    """Input doc string"""
    i = 1
    while i < 60:
        status = rpc_client.get_transactions()
        print(status)
        duration = i * 5
        note = '{} seconds'.format(duration)
        print(note)
        if status == 'Error identifying minting transaction':
            print(
                'Your NFT minting transaction cannot be identified! \nPlease monitor the chia client', '', True)
            break
        elif status == True:
            print('Your NFT has successfully minted!')
            monitor_window(status, note)
            break
        else:
            monitor_window(status, note)
            print('Your NFT is minting, please wait')
            print(status)
            print(i)
        i += 1


def mint_popup(settings, values, filehash, metahash, licensehash):
    """Defines minting confirmation message #to-do add image display to preview"""
    rp = int(values['_RP_']) / 100
    en = values['_EN_']
    ec = values['_EC_']
    url = values['_U_']
    metaurl = values['_MU_']
    licenseurl = values['_LU_']
    message = f"Confirm that you would like to mint this NFT with total cost of 615,000,001 mojo: \n \n Edition: {en} out of {ec} \n \n File URL: {url} \n \n File Hash: {filehash} \n \n MetaData URL: {metaurl} \n \n MetaData Hash: {metahash} \n \n License URL: {licenseurl} \n \n License Hash: {licensehash} \n \n Royalty Percentage: {rp}%"
    mint_confirm(message, values, settings)


def mint_confirm(message, values, settings):  # creates minting confirmation popup
    layout = [[sg.Multiline(message, size=(90, 35))],
              [sg.Button('Confirm'), sg.Button('Cancel/Edit')]]
    eventmint, valuesmint = sg.Window(
        'NFT Minting Confirmation', layout, modal=True, icon=CUSTOM_ICON).read(close=True)
    if eventmint == 'Confirm':
        mint(values, settings)
    else:
        cancel_mint()


def build_dict(settings, values, filehash, metahash, licensehash):
    '''Minting the NFT'''
    jsonerror = ''
    try:
        nft_wallet_did = rpc_client.nft_get_wallet_did(
            settings['nft_wallet_id'])
        nft_data['did_id'] = nft_wallet_did
    except Exception:
        nft_wallet_did = None
        nft_data['did_id'] = nft_wallet_did
        print('No DID is associated with the selected wallet')
        jsonerror = 'No DID is associated with the selected wallet'
    try:
        if settings['nft_wallet_id']:
            nft_data['wallet_id'] = int(settings['nft_wallet_id'])
        else:
            print('error adding wallet ID to json data')
            jsonerror += '\nError adding wallet ID to json data'
        if values['_U_']:
            nft_data['uris'] = url_split(values['_U_'])
        else:
            print('error adding file url to json data')
            jsonerror += '\nError adding file url to json data'
        if filehash:
            nft_data['hash'] = filehash
        else:
            print('error adding file hash to json data')
            jsonerror += '\nError adding file hash to json data'
        if values['_MU_']:
            nft_data['meta_uris'] = url_split(values['_MU_'])
        else:
            print('error adding meta URL to json data')
            jsonerror += '\nError adding meta URL to json data'
        if metahash:
            nft_data['meta_hash'] = metahash
        else:
            print('error adding meta hash to json data')
            jsonerror += '\nError adding meta hash to json data'
        if values['_LU_']:
            nft_data['license_uris'] = url_split(values['_LU_'])
        else:
            print('error adding license URL to json data')
            jsonerror += '\nError adding license URL to json data'
        if licensehash:
            nft_data['license_hash'] = licensehash
        else:
            print('error adding license hash to json data')
            jsonerror += '\nError adding license hash to json data'
        if settings['wallet_address']:
            nft_data['royalty_address'] = settings['wallet_address']
        else:
            print('error adding royalty address to json data')
            jsonerror += '\nError adding royalty address to json data'
        if values['_RP_']:
            nft_data['royalty_percentage'] = int(values['_RP_'])
        else:
            print('error adding royalty percentage to json data')
            jsonerror += '\nError adding royalty percentage to json data'
        if settings['wallet_address']:
            nft_data['target_address'] = settings['wallet_address']
        else:
            print('error adding target wallet to json data')
            jsonerror += '\nError adding target wallet to json data'
        if values['_EN_']:
            nft_data['edition_number'] = int(values['_EN_'])
        else:
            print('error adding edition number to json data')
            jsonerror += '\nError adding edition number to json data'
        if values['_EC_']:
            nft_data['edition_count'] = int(values['_EC_'])
        else:
            print('error adding edition count to json data')
            jsonerror += '\nError adding edition count to json data'
        if not jsonerror:
            data_dump = json.dumps(nft_data)
        else:
            print(jsonerror, '', True)
            data_dump = 'error'
    except Exception:
        print('Could not create json data for NFT! \n Please verify inputs and try again', '', True)

        data_dump = 'error'
    return data_dump


def mint(values, settings):  # formats the json object based on the dict object and submits the RPC command
    if rpc_client.get_sync() == 'Synced':
        filehash, metahash, licensehash = hashing(values)
        data_dump = build_dict(
            settings, values, filehash, metahash, licensehash)
        if data_dump == 'error':
            print(' Error while minting NFT! \n Please check entries and try again: \n{}'.format(
                data_dump), '', True)
        else:
            data = json.loads(data_dump)
            # to-do pull response for transaction, run transaction monitor
            print(data)
            response = rpc_client.nft_mint_nft(data)
            print(response)
            if response['success'] == False:
                print(' Error while minting NFT! \n Please check entries and try again: \n{}\n\n{}'.format(
                    response, data), '', True)
            else:
                #print('Minting NFT: \nThe process can take more than 2 minutes.\nThe NFT will appear in your Chia client once minted', '', True)
                #threading.Thread(target=mint_monitor, args=(), daemon=True).start()
                mint_monitor()
    else:
        print(' Chia instance is not synced \n Please verify your chia instance is synced and reconfirm this mint', '', True)


def cancel_mint():
    '''Cancels minting to allow user to edit information'''
    print('Mint Cancelled by User', '', True)


def create_about_window(settings):
    """About Window"""
    sg.theme(settings['theme'])
    aboutsection = [[text_label1('Developer'), output_text1('NFTr')], [text_label1('Website'), output_text1('https://nftr.pro/')], [text_label1('Discord'), output_text1('https://discord.gg/j7PmvGv5ra')], [
        text_label1('Twitter'), output_text1('https://twitter.com/NFTr_pro')], [text_label1('Github'), output_text1('https://github.com/NFTr/mintingtool')], [text_label1('Email'), output_text1('info@nftr.pro')]]

    column1 = [[sg.Frame('About Mintr', layout=aboutsection, border_width=10)], [
        sg.Button('Close')]]

    return sg.Window('About', column1, size=(425, 250), keep_on_top=True, finalize=True, icon=CUSTOM_ICON)


def create_main_window(settings):
    """Main Program Window """
    sg.theme(settings['theme'])

    # define menu bar and options
    menu_def = [['File', ['Change Settings', 'List Wallet IDs', 'Exit']],
                ['Help', 'About...']]

    # derived from default settings
    header = [[sg.Menu(menu_def, tearoff=False, font='Verdana', pad=(200, 1))],
              [text_label6('Fingerprint'), header_text4(rpc_client.get_fingerprint(), 'Currently Selected Fingerprint'),
               text_label2('NFT Wallet ID'), header_text1(
                   nft_wallet_id, 'Currently Selected NFT Wallet ID'),
               text_label5('Wallet Address'), header_text3(
                   wallet_address, 'Currently Selected Wallet Address'),
               text_label3('DID'), header_text5(rpc_client.nft_get_wallet_did(
                   settings['nft_wallet_id']), 'Currently Selected DID'),
               text_label4('Theme'), header_text2('-THEME-', 'Currently Selected Theme')]]

    # necessary for creating the json used in RPC commands
    onchainmeta = [sg.Frame('On-Chain Metadata',
                            [[text_label1('Edition Number'), output_text3('1', '_EN_', 'This field will not be active until Chia ver 1.5.1 is available (default 1)')],
                             [text_label1('Edition Total'), output_text3(
                                 '1', '_EC_', 'This field will not be active until Chia ver 1.5.1 is available (default 1)')],
                                [text_label1('File URL/URI'), input_text4('_U_',
                                                                          'This NFTs File URI/URL')],
                                [text_label1('Metadata URL/URI'),
                                 input_text4('_MU_', 'This NFTs Metadata URI/URL')],
                                [text_label1('License URL/URI'),
                                 input_text4('_LU_', 'This NFTs License URI/URL')],
                                [text_label1('Royalty Percentage'), input_text5('500', '_RP_', 'This NFTs Royalty Percentage (default 500 = 5%)')]])]

    # to be added once uploading capability is integrated
    offchainmeta = [comingsoon('Off-Chain Metadata', 'Coming Soon',
                               'Off-Chain Metadata will be added once Auto-upload is incorporated')]

    # consolidation of entry fields
    entryfields = [  # [TextLabel('Name'), InputText('_NAME_', 'Note: NFT name will be extracted from off-chain metadata for minting')],
        # [TextLabel('File'), sg.Input(size = inputsize, key='_FILE2_'), sg.FileBrowse(size = textsize1, key='_FILE_')], #to be added once autoupload is integrated
        onchainmeta,
        offchainmeta,
        [comingsoon('License', 'Coming Soon', 'The License will be added once Auto-upload is incorporated')]]

    # image to be added once uploading capability is integrated
    preview = [[sg.Text("", size=(75, 2), key='preview')],
               # [sg.Button(size = (35,22)),
               [sg.Multiline(size=(90, 70), key='-OUTPUT-')]]

    # left column (entry)
    column1 = [[sg.Frame('NFT Entry Fields', layout=entryfields, border_width=10)], [
        sg.Button('Preview')]]

    # right column (preview) - to be migrated to its own popup window once bulk minted is added
    column2 = [[sg.Frame('NFT Preview', layout=preview, border_width=10, size=(
        700, 340))], [sg.Button('Mint NFT')]]

    # define layout with menu, header, and two columns
    layout = [[sg.Frame('Current Settings', layout=header, border_width=10)],
              [sg.Column(column1, element_justification='c'),
              sg.Column(column2, element_justification='c')]]

    # define window
    return sg.Window("MINTr",
                     layout,
                     right_click_menu=right_click_menu,
                     size=(1450, 450),
                     icon=CUSTOM_ICON)


def sync_verify():
    """Sync and network verification"""
    try:
        if rpc_client.get_sync() == 'Synced':
            network_name = rpc_client.get_network()
            if network_name != NETWORK_NAME:
                print(
                    f' Chia instance is operating on {network_name} \n Please migrate your chia instance to {NETWORK_NAME} \n and restart this client', '', True)
        else:
            print(f' Chia instance is not synced \n Please verify your chia instance is synced and restart this client', '', True)
    except Exception:
        print('login_status: ')
        print('Could not contact Chia instance, please make sure it is running and synced')


def main():
    """Event Loop"""
    window, settings = None, load_settings(SETTINGS_FILE, DEFAULT_SETTINGS)

    while True:             # Event Loop
        if window is None:
            window = create_main_window(settings)
            sync_verify()
            #threading.Thread(target=the_thread, args=(), daemon=True).start()

        event, values = window.read()
        # break if window closed or other exit event
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        # process output
        if event == 'Preview':
            # loading(10000) #to-do add loading gif into thread
            print('starting output refresh')
            refresh(settings, window, values)
        if event == 'Mint NFT':
            # loading(10000) #to-do add loading gif into thread
            filehash, metahash, licensehash = refresh(settings, window, values)
            mint_popup(settings, values, filehash, metahash, licensehash)
        # change settings
        if event == 'List Wallet IDs':
            wallet_popup()
        if event in ('Change Settings', 'Settings'):
            event, values = create_settings_window(settings).read(close=True)
            if event == 'Save':
                window.close()
                window = None
                save_settings(SETTINGS_FILE, settings, values)
            elif event in (sg.WIN_CLOSED, 'Exit'):
                window.close()
                window = None
                print('Settings window closed without saving', '', True)
        # about window
        if event == 'About...':
            event, values = create_about_window(settings).read(close=True)
    window.close()


if __name__ == "__main__":
    main()
