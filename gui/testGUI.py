import PySimpleGUI as sg
from sha256_hash import sha256Checksum as FileHash
import rpc_client
#from PIL import Image
import requests
from io import BytesIO
import json
from json import (load as jsonload, dump as jsondump)
import threading
import time
import sys
import config
from os import path

########################################## Define Defaults ##########################################
loadingGIF = config.LOADING_GIF

THREAD_EVENT = '-THREAD-'
SETTINGS_FILE = path.join(path.dirname(__file__), r'settings_file.cfg')
DEFAULT_SETTINGS = {'fingerprint': 0xdeadbeef, 'nft_wallet_id': None , 'wallet_address': None , 'did': None , 'theme': sg.theme()}
# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {'fingerprint': '-FINGERPRINT-', 'nft_wallet_id': '-NFT WALLET ID-' , 'wallet_address': '-WALLET ADDRESS-' , 'did': '-DID-' , 'theme': '-THEME-'}

nft_data = {"wallet_id": 3,   # 3 is default as this should be the NFT wallet if no additional wallets have been created
            "uris": [""],
            "hash": "",
            "meta_uris" : [""],
            "meta_hash": "",
            "license_uris": [""],
            "license_hash": "",
            "royalty_address": "",
            "royalty_percentage": 5,   #5 is the default
            "target_address": "",
            "edition_number": 1,  #1/1 editions are default
            "edition_count": 1,  #1/1 editions are default
            "fee": 615000000}   #min recommended minting fee is deafult

########################################## Define Threading ##########################################
def the_thread(window, values):
    """
    The thread that communicates with the application through the window's events.

    Once a second wakes and sends a new event and associated value to the window
    """
    while True:
        print(rpc_client.get_sync())
        time.sleep(3)


########################################## Define Text Sizes ##########################################
inputsize = (25,3)
textsize1 = (5,1)
textsize2 = (10,1)
textsize3 = (22,1)
textsize4 = (80,1)

########################################## Define Text Boxes and Popups ##########################################
def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))
def OutputText1(text): return sg.InputText(text, use_readonly_for_disable=True, disabled=True, disabled_readonly_background_color=sg.theme_text_element_background_color())

def HeaderText1(key, tooltip): return sg.Text(key=key, size=(5,1), tooltip=tooltip)
def HeaderText2(key, tooltip): return sg.Text(key=key, size=(15,1), tooltip=tooltip)
def HeaderText3(key, tooltip): return sg.Text(key=key, size=(30,1), tooltip=tooltip)

def InputText(key, tooltip): return sg.Input(key=key, size=inputsize, tooltip=tooltip)
def InputText1(key, tooltip): return sg.Input(key=key, size=textsize1, tooltip=tooltip)
def InputText2(key, tooltip): return sg.Input(key=key, size=textsize2, tooltip=tooltip)
def InputText3(key, tooltip): return sg.Input(key=key, size=textsize3, tooltip=tooltip)
def InputText4(key, tooltip): return sg.Input(key=key, size=textsize4, tooltip=tooltip)

def ComingSoon(title, text, tooltip): return sg.Frame(title ,[[sg.Text(text, size = textsize2, tooltip=tooltip)]])

def Popup(message, title, notitle): return sg.popup(message, title = title, no_titlebar = notitle, keep_on_top = True)

def PopupQuick(message): return sg.popup_quick_message(message, keep_on_top=True, background_color='red', text_color='white', no_titlebar = True)

########################################## Load/Save Settings File ##########################################
def load_settings(settings_file, default_settings):
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
    except Exception as e:
        PopupQuick(f'exception {e}' 'No settings file found... will create one for you') #to-do add settings for network, chia install root, etc
        settings = default_settings
        save_settings(settings_file, settings, None)
    return settings

def refresh_settings(settings, window, values):
    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
        except Exception as e:
            print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

def save_settings(settings_file, settings, values):
    if values:      # if there are stuff specified by another window, fill in those values
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
            try:
                window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
            except Exception as e:
                print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)

    print('Settings saved', '', True)

########################################## Define File Hashing ##########################################
def file_hash(list):
    hash = ''
    u = 0
    hash_list = []
    print('hashing url list: {} with length: {}'.format(list[0], len(list[0])))
    while u < len(list[0]):
        print('attempting hash for {}'.format(list[0][u]))
        hash = FileHash(None, str(list[0][u]))
        hash_list.append(hash)
        print('hash list: {}'.format(hash_list))
        if u > 0: #separate into own function and iterate though full hash list at once
            if hash_list[u] == hash_list[0]:
                print('hash #{} matches the first url file hash'.format(u+1))
                hash_verify = hash_list[0]
            else:
                print('hash #{} does not match the first url file hash\n'.format(u+1))
                print('first file hash: {}'.format(hash_list[0]))
                print('mismatched file hash: {}'.format(hash_list[u]))
                hash_verify = 'hash #{} does not match the first url file hash'.format(u+1)
        else:
            hash_verify = hash_list[0]
        u = u + 1
    return hash_verify

def hashing(values):
    try:
        list = url_split(values['_U_'])   # Verifies URLs are entered for each field, to-do iterate over list of fields
        fileHash = file_hash(list)
    except Exception as e:
        print('error deriving file hash, please verify url(s)')
        fileHash = 'error'
    try:
        list = url_split(values['_MU_'])
        metaHash = file_hash(list)
    except Exception as e:
        print('error deriving metafile hash, please verify url(s)')
        metaHash = 'error'
    try:
        list = url_split(values['_LU_'])
        licenseHash = file_hash(list)
    except Exception as e:
        print('error deriving license hash, please verify url(s)')
        licenseHash = 'error'
    return fileHash, metaHash, licenseHash

def url_split(url):  # splits urls prio to file hashing if multiple are present and separated with commas
    try:
        print('attempting url split for {}'.format(url))
        list = url.replace(" ", "")
        list = [list.split(',')] #to-do add handling for blank entries after comma
        print(len(list[0]))
    except Exception as e:
        print('URL split failed')
        list = url
    return list

########################################## Define Page Refresh ##########################################
def refresh(settings, window, values):
    print(values)
    print(rpc_client.get_sync())
    message, fileHash, metaHash, licenseHash = page_refresh(settings, window, values)
    window['-OUTPUT-'].update(message)   # updates preview window
    return fileHash, metaHash, licenseHash

def page_refresh(settings, window, values):
    message = ''
    print('running refresh')
    refresh_settings(settings, window, values)
    fileHash, metaHash, licenseHash = hashing(values)
    message = "{} \n Edition: {} out of {} \n File URL: {} \n File Hash: {} \n MetaData URL: {} \n MetaData Hash: {} \n License URL: {} \n License Hash: {} \n Royalty Percentage: {}% \n Minting Fees: 65,000,001 Mojo".format(values['_NAME_'], values['_EN_'], values['_EC_'], values['_U_'], fileHash, values['_MU_'], metaHash, values['_LU_'], licenseHash, values['_RP_'])
    return message, fileHash, metaHash, licenseHash


def refresh_thread(settings, window, values):  # to-do resolve threading issues
    #threading.Thread(target=refresh, args=(settings, window, values), daemon=True).start()
    time.sleep(4)
    return refreshing

########################################## Minting Confirmations  ##########################################
def mint_popup(settings, values, fileHash, metaHash, licenseHash): #defines minting confirmation message
    message = "Confirm that you would like to mint this NFT with total cost of 615,000,001 mojo: \n {} \n Edition: {} out of {} \n File URL: {} \n File Hash: {} \n MetaData URL: {} \n MetaData Hash: {} \n License URL: {} \n License Hash: {} \n Royalty Percentage: {}%".format(values['_NAME_'], values['_EN_'], values['_EC_'], values['_U_'], fileHash, values['_MU_'], metaHash, values['_LU_'], licenseHash, values['_RP_'])
    mint_confirm(message, values, settings)

def mint_confirm(message, values, settings): #creates minting confirmation popup
    layout = [[sg.Text(message)],
             [sg.Button('Confirm'), sg.Button('Cancel/Edit')]]
    eventMint, valuesMint = sg.Window('NFT Minting Confirmation', layout, modal=True).read(close=True)
    if eventMint == 'Confirm':
        mint(values, settings)
    else:
        cancel_mint()

########################################## Minting the NFT  ##########################################
def mint_nft(settings, values, fileHash, metaHash, licenseHash): #creates the necessary dict object for minting
    try:
        nft_data['wallet_id'] = int(settings['nft_wallet_id'])
        nft_data['uris'][0] = str(values['_U_'])
        nft_data['hash'] = fileHash
        nft_data['meta_uris'][0] = str(values['_MU_'])
        nft_data['meta_hash'] = metaHash
        nft_data['license_uris'][0] = str(values['_LU_'])
        nft_data['license_hash'] = licenseHash
        nft_data['royalty_address'] = settings['wallet_address']
        nft_data['royalty_percentage'] = values['_RP_']
        nft_data['target_address'] = settings['wallet_address']
        nft_data['edition_number'] =  int(values['_EN_'])
        nft_data['edition_count'] = int(values['_EC_'])
        data_dump = json.dumps(nft_data)
    except Exception as e:
        print('could not create json data, please verify inputs and try again')
    return data_dump

def mint(values, settings): #formats the json object based on the dict object and submits the RPC command
    fileHash, metaHash, licenseHash = hashing(values)
    data_dump = mint_nft(settings, values, fileHash, metaHash, licenseHash)
    data = "'" + data_dump + "'"
    print(data)
    Popup('Minting NFT', '', True)

def cancel_mint(): #cancels minting to allow user to edit information
    print("Mint Cancelled by User")

########################################## Settings Window ##########################################
def create_settings_window(settings):
    sg.theme(settings['theme'])

    layout = [[sg.Text('Settings', font='Any 15')],
             [TextLabel('Fingerprint'), sg.Input(key='-FINGERPRINT-')],
             [TextLabel('NFT Wallet ID'),sg.Input(key='-NFT WALLET ID-')],
             [TextLabel('Wallet Address'),sg.Input(key='-WALLET ADDRESS-')],
             [TextLabel('DID'),sg.Input(key='-DID-')],
             [TextLabel('Theme'),sg.Combo(sg.theme_list(), size=(20, 20), key='-THEME-')],
             [sg.Button('Save'), sg.Button('Exit')]]

    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
        except Exception as e:
            Popup('Problem updating PySimpleGUI window from settings. Key = {key}', '', True)

    return window

########################################## About Window ##########################################
def create_about_window(settings):
    sg.theme(settings['theme'])

    aboutSection = [[TextLabel('Developer'), OutputText1('NFTr')],
                   [TextLabel('Website'), OutputText1('https://nftr.pro/')],
                   [TextLabel('Discord'), OutputText1('https://discord.gg/j7PmvGv5ra')],
                   [TextLabel('Twitter'), OutputText1('https://twitter.com/NFTr_pro')],
                   [TextLabel('Github'), OutputText1('https://github.com/NFTr/mintingtool')],
                   [TextLabel('Email'), OutputText1('info@nftr.pro')]]


    column1 = [[sg.Frame('About Mintr', layout = aboutSection, border_width=10)], [sg.Button('Close')]]

    window = sg.Window('About', column1, size=(425,250), keep_on_top=True, finalize=True)

    return window

########################################## Loading GIF ##########################################
def loading(loadingGIF, time): #to-do add in main loop as a subprocess or thread
    for i in range(time):
        sg.PopupAnimated(loadingGIF, background_color='white', time_between_frames=100)
    sg.PopupAnimated(None)

def loading_thread(loadingGIF, time):
    threading.Thread(target=loading, args=(loadingGIF, time), daemon=True).start()

########################################## Main Program Window ##########################################
def create_main_window(settings):
    sg.theme(settings['theme'])

    #define menu bar and options
    menu_def = [['File', ['Change Settings', 'Exit']],
                ['Help', 'About...']]

    #define menu bar and options, to-do add functionality of right click menu
    right_click_menu = ['Unused', ['Cut', 'Copy', 'Paste', 'About']]

    #derived from default settings
    header = [[sg.Menu(menu_def, tearoff=False, font='Verdana', pad=(200, 1))],
              [TextLabel('Fingerprint'), HeaderText1('-FINGERPRINT-', 'Currently Selected Fingerprint'),
               TextLabel('NFT Wallet ID'), HeaderText1('-NFT WALLET ID-', 'Currently Selected NFT Wallet ID'),
               TextLabel('Wallet Address'), HeaderText3('-WALLET ADDRESS-', 'Currently Selected Wallet Address'),
               TextLabel('DID'), HeaderText3('-DID-', 'Currently Selected DID'),
               TextLabel('Theme'), HeaderText2('-THEME-', 'Currently Selected Theme')]]

    #necessary for creating the json used in created RPC commands
    onchainmeta = [sg.Frame('On-Chain Metadata',
                  [[TextLabel('Edition Number'), InputText2('_EN_', 'This NFTs Edition Number (default 1)')],
                   [TextLabel('Edition Total'), InputText2('_EC_', 'Total Editions of this NFT (default 1)')],
                   [TextLabel('File URL/URI'), InputText4('_U_', 'This NFTs File URI/URL')],
                   [TextLabel('Metadata URL/URI'), InputText4('_MU_', 'This NFTs Metadata URI/URL')],
                   [TextLabel('License URL/URI'), InputText4('_LU_', 'This NFTs License URI/URL')],
                   [TextLabel('Royalty Percentage'), InputText2('_RP_', 'This NFTs Royalty Percentage (default 5 = 5%)')]])]

    #to be added once uploading capability is integrated
    offchainmeta = [ComingSoon('Off-Chain Metadata', 'Coming Soon', 'Off-Chain Metadata will be added once Auto-upload is incorporated')]

    #consolidation of entry fields
    entryFields = [[TextLabel('Name'), InputText('_NAME_', 'Note: NFT name will be extracted from off-chain metadata for minting')],
                  #[TextLabel('File'), sg.Input(size = inputsize, key='_FILE2_'), sg.FileBrowse(size = textsize1, key='_FILE_')], #to be added once autoupload is integrated
                  onchainmeta,
                  offchainmeta,
                  [ComingSoon('License', 'Coming Soon', 'The License will be added once Auto-upload is incorporated')]]

    #image to be added once uploading capability is integrated
    preview = [[sg.Text("", size = (75,2),key = 'preview')],
               #[sg.Button(size = (35,22)),
               [sg.Multiline(size = (90, 70),key = '-OUTPUT-')]]

    #left column (entry)
    column1 = [[sg.Frame('NFT Entry Fields', layout = entryFields, border_width=10)], [sg.Button('Preview')]]

    #right column (preview) - to be migrated to its own popup window once bulk minted is added
    column2 = [[sg.Frame('NFT Preview', layout = preview, border_width=10, size = (700, 340))], [sg.Button('Mint NFT')]]

    #define layout with menu, header, and two columns
    layout = [[sg.Frame('Current Settings', layout = header, border_width=10)],
              [sg.Column(column1, element_justification='c'),
              sg.Column(column2, element_justification='c')]]

    #define window
    return sg.Window("MINTr",
                      layout,
                      right_click_menu=right_click_menu, size=(1450,450))

########################################## Event Loop ##########################################
def main():
    window, settings = None, load_settings(SETTINGS_FILE, DEFAULT_SETTINGS)

    while True:   #Event loop
        if window is None:
            window = create_main_window(settings)

        event, values = window.read()
        #break if window closed or other exit event
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        else:
            #process output
            if event == 'Preview':
                print('starting')
                refresh(settings, window, values)
                #loading(loadingGIF, 3500) #to-do add loading gif into thread
                #refresh_thread(settings, window, values)
            #mint NFT popup
            if event == 'Mint NFT':
                #loading(loadingGIF, 10000) #to-do add loading gif into thread
                fileHash, metaHash, licenseHash = refresh(settings, window, values)
                mint_confirmed = mint_popup(settings, values, fileHash, metaHash, licenseHash)
            #change settings
            if event in ('Change Settings', 'Settings'):
                event, values = create_settings_window(settings).read(close=True)
                if event == 'Save':
                    window.close()
                    window = None
                    save_settings(SETTINGS_FILE, settings, values)
                elif event in (sg.WIN_CLOSED, 'Exit'):
                    window.close()
                    window = None
                    Popup('Settings window closed without saving', '', True)
            #about window
            if event == 'About...':
                event, values = create_about_window(settings).read(close=True)
    window.close()
main()
