import json
import socket
from graphics import *
import argparse
from queue import Queue
from typing import List


class Pin(Circle):
    def __init__(self, center: Point, radius: int):
        super().__init__(center, radius)


class Note(Button):
    def __init__(self, colour: str, message: str, is_pinned: bool, P1: Point, P2: Point, win: GraphWin, id: str):
        self.colour = colour
        self.message = message
        self.pinned = is_pinned
        self.pins: List[Pin] = []
        super().__init__(P1, P2, message, win)
        self.setButtonFill(colour)

    """
    Server Implementation
    """

    def pin(self, p: Pin):
        self.pins.append(p)
        self.pinned = True
        return

    def unpin(self, p: Pin):
        if (len(self.pins) == 0):
            return
        if p in self.pins:
            self.pins.remove(p)
            p.undraw()

        if (len(self.pins) == 0):
            self.pinned = False
            self.undraw()


DEF_HOST = '0.0.0.0'
DEF_PORT = 5000
BUFFER = 1024
UI_STEP = 60

# * Sample commands
# ? POST 2 3 white Meeting next Wednesday from 2 to 3
# ? SHAKE
# ? CLEAR
# ? DISCONNECT
# ? GET color=<color> contains=<x> <y> refersTo=<substring>
# ? PIN <x> <y>
# ? UNPIN <x> <y>


def start_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ? Does this need to be a queue?
    notes = []
    # Connect to the server
    client.connect((host, port))

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

    def redraw_board():
        for n in notes:
            n.undraw()
        notes.clear()

        # Re-fetch data
        client.sendall("GET None None None None".encode('utf-8'))
        raw = client.recv(BUFFER).decode('utf-8')
        boardNotes = json.loads(raw)

        for noteData in boardNotes:
            P1 = Point(noteData["x"], noteData["y"])
            P2 = Point(noteData["x"] + noteWidth, noteData["y"] + noteHeight)
            note = Note(noteData["colour"], noteData["text"],
                        noteData["pinned"], P1, P2, win, noteData["id"])
            note.draw()
            notes.append(note)

    # * The window for the GUI
    win = GraphWin("CP372 - A01", boardWidth, boardHeight)

    # * Define Buttons
    clearButton = Button(Point(20, 20), Point(100, 60), "CLEAR", win).draw()
    disconnectButton = Button(Point(20, 80), Point(
        100, 120), "DISCONNECT", win).setFontSize(8).draw()
    shakeButton = Button(Point(20, 80 + UI_STEP),
                         Point(100, 120+UI_STEP), "SHAKE", win)
    mode = "NOTE"
    toggleButton = Button(Point(20, 140), Point(
        100, 180), f"Mode: {mode}", win).setFontSize(8).draw()
    while True:
        x = win.getMouse()
        if (clearButton.clicked(x)):
            client.sendall("CLEAR".encode("utf-8"))
            redraw_board()
            pass
        elif (shakeButton.clicked(x)):
            client.sendall('SHAKE'.encode('utf-8'))
            redraw_board()
            pass
        elif (disconnectButton.clicked(x)):
            client.sendall('DISCONNECT'.encode('utf-8'))
            #! Safe exit, need to make sure we close the thread !

            # * We can safely close the UI
            win.close()
            print('Closing the GUI....')
            return
        elif toggleButton.clicked(x):
            mode = "PIN" if mode == "NOTE" else "NOTE"
            toggleButton.setText(f"Mode: {mode}")
            continue
        else:
            if (mode == "NOTE"):
                # Create a new note
                x_position, y_position = x.getX(), x.getY()
                #! will have to enter through the terminal.
                text = input("Enter note text: ")

                # TODO: Needs to be verified somewhere.
                # TODO: pretty simple if (color not in coloursArray)
                colour = input("Enter a colour: ")

                # TODO: Verify overlap, complete overlap xOfSomeExistingNote=newX and
                # TODO: yOfSomeExistingNote=newY but should this be defined server side?

                # ? This is subject to change.
                cmd = f'POST {x_position} {y_position} {colour} {text}'

                client.sendall(cmd.encode('utf-8'))
                redraw_board()
                continue
            elif (mode == 'PIN'):
                for n in notes:
                    if (n.clicked(x)):
                        if (n.pinned):
                            client.sendall(f"UNPIN {n.id}".encode('utf-8'))
                            n.pinned = False
                        else:
                            client.sendall(f"PIN {n.id}".encode('utf-8'))
                        break
                redraw_board()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default=DEF_HOST)
    parser.add_argument('--port', type=int, default=DEF_PORT)
    args = parser.parse_args()
    print(args.host)
    start_client(args.host, args.port)
