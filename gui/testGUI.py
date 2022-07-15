import PySimpleGUI as sg
from json import (load as jsonload, dump as jsondump)
from os import path

"""
    A simple "settings" implementation.  Load/Edit/Save settings for your programs
    Uses json file format which makes it trivial to integrate into a Python program.  If you can
    put your data into a dictionary, you can save it as a settings file.

    Note that it attempts to use a lookup dictionary to convert from the settings file to keys used in
    your settings window.  Some element's "update" methods may not work correctly for some elements.

    Copyright 2020 PySimpleGUI.com
    Licensed under LGPL-3
"""

SETTINGS_FILE = path.join(path.dirname(__file__), r'settings_file.cfg')
DEFAULT_SETTINGS = {'fingerprint': 0xdeadbeef, 'nft_wallet_id': None , 'wallet_address': None , 'did': None , 'theme': sg.theme()}
# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {'fingerprint': '-FINGERPRINT-', 'nft_wallet_id': '-NFT WALLET ID-' , 'wallet_address': '-WALLET ADDRESS-' , 'did': '-DID-' , 'theme': '-THEME-'}

NFT_DATA_FILE = path.join(path.dirname(__file__), r'nft_data_file.json')
DEFAULT_NFT_DATA = {'wallet_id': None, 'royalty_address': None , 'target_address': None , 'hash': None, 'uris': [], 'meta_hash': None, 'meta_uris': [], 'license_hash': None, 'license_uris': [], 'series_total': 1, 'series_number': 1, 'fee': 0, 'royalty_percentage': 1500}
# "Map" from the settings dictionary keys to the window's element keys
NFT_DATA_KEYS_TO_ELEMENT_KEYS = {'wallet_id': '-WALLET ID-', 'royalty_address': '-ROYALTY ADDRESS-' , 'target_address': '-TARGET ADDRESS-' , 'hash': '-HASH-', 'uris': '-URIS-', 'meta_hash': '-META HASH-', 'meta_uris': '-META URIS-', 'license_hash': '-LICENSE HASH-', 'license_uris': '-LICENSE URIS-', 'series_total': '-SERIES TOTAL-', 'series_number': '-SERIES NUMBER-', 'fee': '-FEE-', 'royalty_percentage': '-ROYALTY FEE-'}


def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))

########################################## Load/Save Settings File ##########################################
def load_settings(settings_file, default_settings, nft_data_file, default_nft_data):
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
    except Exception as e:
        sg.popup_quick_message(f'exception {e}', 'No settings file found... will create one for you', keep_on_top=True, background_color='red', text_color='white')
        settings = default_settings
        save_settings(settings_file, settings, None)
    return settings
    try:
        with open(nft_data_file, 'r') as f:
            nft_data = jsonload(f)
    except Exception as e:
        sg.popup_quick_message(f'exception {e}', 'No data file found... default data will be created for you', keep_on_top=True, background_color='red', text_color='white')
        nft_data = default_nft_data
        save_nft_data(nft_data_file, nft_data, None)
    return nft_data


def save_settings(settings_file, settings, values):
    if values:      # if there are stuff specified by another window, fill in those values
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:  # update window with the values read from settings file
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f'Problem updating settings from window values. Key = {key}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)

    sg.popup('Settings saved')

########################################## Save JSON Data File ##########################################
def save_nft_data(nft_data_file, nft_data, values):
    if values:      # if there are stuff specified by another window, fill in those values
        for key in NFT_DATA_KEYS_TO_ELEMENT_KEYS:  # update window with the values read from settings file
            try:
                nft_data[key] = values[NFT_DATA_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f'Problem updating settings from window values. Key = {key}')

    with open(nft_data_file, 'w') as f:
        jsondump(nft_data, f)

    sg.popup('NFT data saved')

########################################## Make a settings window ##########################################
def create_settings_window(settings):
    sg.theme(settings['theme'])

    layout = [  [sg.Text('Settings', font='Any 15')],
                [TextLabel('Fingerprint'), sg.Input(key='-FINGERPRINT-')],
                [TextLabel('NFT Wallet ID'),sg.Input(key='-NFT WALLET ID-')],
                [TextLabel('Wallet Address'),sg.Input(key='-WALLET ADDRESS-')],
                [TextLabel('DID'),sg.Input(key='-DID-')],
                [TextLabel('Theme'),sg.Combo(sg.theme_list(), size=(20, 20), key='-THEME-')],
                [sg.Button('Save'), sg.Button('Exit')]  ]

    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
        except Exception as e:
            print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

    return window

########################################## Main Program Window & Event Loop ##########################################
def create_main_window(settings):
    sg.theme(settings['theme'])

    #define menu bar and options
    menu_def = [['File', ['Change Settings', 'Exit']],
                ['Help', 'About...']]

    right_click_menu = ['Unused', ['Cut', 'Copy', 'Paste', 'About']]

    #define different text sizes (input boxes are separate)
    inputsize = (25,3)
    textsize1 = (5,1)
    textsize2 = (10,1)
    textsize3 = (22,1)

    #derived from default settings
    header = [[sg.Menu(menu_def, tearoff=False, font='Verdana', pad=(200, 1))],
              [TextLabel('Fingerprint'),
               sg.Text(size = textsize3, key = '-FINGERPRINT-'),
               TextLabel('NFT Wallet ID'),
               sg.Text(size = textsize2, key = '-NFT WALLET ID-'),
               TextLabel('Wallet Address'),
               sg.Text(size = textsize3, key = '-WALLET ADDRESS-'),
               TextLabel('DID'),
               sg.Text(size = textsize3, key = '-DID-'),
               TextLabel('Theme'),
               sg.Text(size = textsize2, key = '-THEME-')]]

    #necessary for creating the json used in created RPC commands
    onchainmeta = [sg.Frame('On-Chain Metadata',[[TextLabel('Series Number'), sg.Input(key='_SN_')],
                   [TextLabel('Series Total'), sg.Input(key='_ST_')],
                   [TextLabel('File URL/URI'), sg.Input(key='_U_')],
                   [TextLabel('Metadata URL/URI'), sg.Input(key='_MU_')],
                   [TextLabel('License URL/URI'), sg.Input(key='_LU_')]])]

    #to be added once uploading capability is integrated
    offchainmeta = [sg.Frame('Off-Chain Metadata',[[sg.Text('Coming Soon', size = textsize2)]])]


    #consolidation of entry fields
    entryFields = [[TextLabel('Name'), sg.Input(size = inputsize, key='_NAME_'), sg.Text('Note: NFT name will be extracted from off-chain metadata for minting')],
                  #[TextLabel('File'), sg.Input(size = inputsize, key='_FILE2_'), sg.FileBrowse(size = textsize1, key='_FILE_')],
                  onchainmeta,
                  offchainmeta,
                  [sg.Frame('License',[[sg.Text('Coming Soon', size = textsize2)]])]]

    #image to be added once uploading capability is integrated
    preview = [[sg.Text("", size = (75,2),key = 'preview')],
               [sg.Text(key = '-OUTPUT-')]]

    #left column (entry)
    column1 = [[sg.Frame('NFT Entry Fields', layout = entryFields, border_width=10)], [sg.Button('Preview')]]

    #right column (display)
    column2 = [[sg.Frame('NFT Preview', layout = preview, border_width=10)]]

    #define layout with menu, header, and two columns
    layout = [[sg.Frame('Current Settings', layout = header, border_width=10)],
              [sg.Column(column1, element_justification='c'),
              sg.Column(column2, element_justification='c')]]

    #define window
    return sg.Window("MINTr",
                      layout,
                      right_click_menu=right_click_menu)

def main():
    window, settings = None, load_settings(SETTINGS_FILE, DEFAULT_SETTINGS, NFT_DATA_FILE, DEFAULT_NFT_DATA)

    while True:             # Event Loop
        if window is None:
            window = create_main_window(settings)

        event, values = window.read()
        #break if window closed or other exit event
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        #process output
        if event == 'Preview':
            for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
                try:
                    window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
                except Exception as e:
                    print(f'Problem updating PySimpleGUI window from settings. Key = {key}')
            window['-OUTPUT-'].update(values['_NAME_'] + '\n'
                    + "Number " + values['_SN_'] + " out of " + values['_ST_'] + '\n'
                    + "File URL: " + values['_U_'] + '\n'
                    + "MetaData URL: " + values['_MU_'] + '\n'
                    + "License URL: " + values['_LU_'])
        #change settings
        if event in ('Change Settings', 'Settings'):
            event, values = create_settings_window(settings).read(close=True)
            if event == 'Save':
                window.close()
                window = None
                save_settings(SETTINGS_FILE, settings, values)
        #interact with data
        if event in ('Load Data', 'Data'):
            event, values = create_nft_data_window(nft_data).read(close=True)
            if event == 'Save':
                window.close()
                window = None
                save_nft_data(NFT_DATA_FILE, nft_data, values)
    window.close()


main()
