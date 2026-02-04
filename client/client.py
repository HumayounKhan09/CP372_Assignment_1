import json
import socket
from graphics import *

DEF_HOST = ''  # 127.0.0.1?
DEF_PORT = 9000
BUFFER = 1024


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client.connect((DEF_HOST or '127.0.0.1', DEF_PORT))

    # Parse JSON for the data
    raw_settings = client.recv(BUFFER)
    if not raw_settings:
        print("No data")
        return
    boardWidth, boardHeight, noteHeight, noteWidth, colours = json.loads(
        raw_settings.decode('utf-8'))
    print(f'Board w = {boardWidth} x h = {boardHeight}')
    print(f'Note  w = {noteWidth} x h = {noteHeight}')
    print(f'{colours}')

    win = GraphWin("TITLE GOES HERE", boardWidth, boardHeight)
    # Define the GUI
    clearButton = Button(Point(20, 20), Point(100, 60), "CLEAR", win).draw()
    disconnectButton = Button(
        Point(20, 80), Point(100, 120), "DISCONNECT", win).setFontSize(8).draw()

    # Define the input
    portEntry = Entry(Point(boardWidth-50, 20), 10).draw(win)
    ipEntry = Entry(Point(boardWidth-50, 40), 10).draw(win)

    while True:
        x = win.getMouse()
        if (clearButton.clicked(x)):
            client.sendall("CLEAR".encode("utf-8"))
            pass
        elif (disconnectButton.clicked(x)):
            client.sendall('DISCONNECT'.encode('utf-8'))
            # disconnect
            pass


if __name__ == "__main__":
    start_client()
