import PySimpleGUI as sg
from PIL import ImageTk, Image
from PySimpleGUI.PySimpleGUI import Column, HorizontalSeparator, In, VSeperator
from io import BytesIO
import io
import os
import requests
import cloudscraper

url = "https://bafybeibir7dkzgiiz7tuhgbvvaxag6uyo7ft6ivaeyuqqftnwcmcieifhi.ipfs.nftstorage.link/player1.gif"
response = requests.get(url, stream=True)
response.raw.decode_content = True
# img = ImageQt.Image.open(response.raw)
# data = image_to_data(img)


def main():
    layout = [
        [sg.Image(data=response.raw.read(), size=(50,50))],
        [
            sg.Text("Image File"),
            sg.Input(size=(25, 1), key="-FILE-"),
            sg.Button("Load Image"),
        ],
    ]
    window = sg.Window("Image Viewer", layout)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    window.close()
if __name__ == "__main__":
    main()
