import PySimpleGUI as sg
import json

def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))

onChainMeta = [['item',['Edition Number'],['key']]]

#data = json.loads(onChainMeta)

# make Header larger
layout = [[sg.Text('Astronomy Quiz #1', font='ANY 15', size=(30, 2))]]

# "generate" the layout for the window based on the Question and Answer information
for tag in onChainMeta:
    item = tag[0]
    k = tag[1]
    tt = tag[0]
    layout += [[TextLabel(item), sg.Input(key=k, tooltip=tt)]]

window = sg.Window('To Do List Example', layout)

event, values = window.read()
