import json
import socket
from graphics import *

DEF_HOST = ''  # 127.0.0.1?
DEF_PORT = 9000
BUFFER = 1024
UI_STEP = 60


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client.connect((DEF_HOST or '127.0.0.1', DEF_PORT))

    # Parse JSON for the data
    raw_settings = client.recv(BUFFER)

    # If there's no data, just close the client
    if not raw_settings:
        print("No data")
        return

    # Get the JSON config from the server
    boardWidth, boardHeight, noteHeight, noteWidth, colours = json.loads(
        raw_settings.decode('utf-8'))

    #! Can be removed later
    print(f'Board w = {boardWidth} x h = {boardHeight}')
    print(f'Note  w = {noteWidth} x h = {noteHeight}')

    # * Array of colours
    arrColours = colours.split(' ')
    print(f'{arrColours}')

    # * The window for the GUI
    win = GraphWin("CP372 - A01", boardWidth, boardHeight)

    # * Define Buttons
    clearButton = Button(Point(20, 20), Point(100, 60), "CLEAR", win).draw()
    disconnectButton = Button(Point(20, 80), Point(
        100, 120), "DISCONNECT", win).setFontSize(8).draw()
    shakeButton = Button(Point(20, 80 + UI_STEP),
                         Point(100, 120+UI_STEP), "SHAKE", win)

    # * Define the input
    portEntry = Entry(Point(boardWidth-50, 20), 10).draw(win)
    ipEntry = Entry(Point(boardWidth-50, 40), 10).draw(win)

    while True:
        x = win.getMouse()
        if (clearButton.clicked(x)):
            client.sendall("CLEAR".encode("utf-8"))
            pass
        elif (shakeButton.clicked(x)):
            client.sendall('SHAKE'.encode('utf-8'))
            pass
        elif (disconnectButton.clicked(x)):
            client.sendall('DISCONNECT'.encode('utf-8'))
            # Safe exit, need to make sure we close the thread !
            pass


if __name__ == "__main__":
    start_client()
