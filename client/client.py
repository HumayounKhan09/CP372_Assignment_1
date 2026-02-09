import json
import socket
from graphics import *
import argparse
from typing import List


class Pin(Circle):
    def __init__(self, center: Point, radius: int):
        super().__init__(center, radius)


class Note(Button):
    def __init__(self, colour: str, message: str, is_pinned: bool,
                 P1: Point, P2: Point, win: GraphWin, id: str):
        self.colour = colour
        self.message = message
        self.pinned = is_pinned
        self.pins: List[Pin] = []
        super().__init__(P1, P2, message, win)
        self.setButtonFill(colour)


DEF_HOST = '0.0.0.0'
DEF_PORT = 5000
BUFFER = 1024
UI_STEP = 60
PIN_RADIUS = 4
PIN_CLICK_RADIUS2 = 12 * 12   # distance² tolerance


def start_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    notes: List[Note] = []
    pins: List[Pin] = []

    raw_settings = client.recv(BUFFER)
    if not raw_settings:
        print("No server data")
        return

    boardWidth, boardHeight, noteHeight, noteWidth, colours = json.loads(
        raw_settings.decode("utf-8")
    )

    print(f"Board: {boardWidth}x{boardHeight}")
    print(f"Note:  {noteWidth}x{noteHeight}")

    win = GraphWin("CP372 - A01", boardWidth, boardHeight)

    def clear_pins():
        for p in pins:
            p.undraw()
        pins.clear()

    def redraw_pins():
        clear_pins()

        client.sendall(b"GET_PINS")
        raw = client.recv(BUFFER).decode("utf-8").strip()

        if raw.startswith("ERROR"):
            return

        lines = raw.splitlines()
        if lines[0] != "OK" or lines[-1] != "END":
            print("Malformed GET_PINS")
            return

        for line in lines[1:-1]:
            try:
                _, x, y = line.split()
                x = int(x)
                y = int(y)

                p = Pin(Point(x, y), PIN_RADIUS)
                p.setFill("black")
                p.draw(win)
                pins.append(p)
            except ValueError:
                print("Bad pin line:", line)

    def redraw_board():
        for n in notes:
            n.undraw()
        notes.clear()

        client.sendall(b"GET None None None None")
        raw = client.recv(BUFFER).decode("utf-8").strip()

        if raw.startswith("ERROR"):
            print(raw)
            return

        lines = raw.splitlines()
        if lines[0] != "OK" or lines[-1] != "END":
            print("Malformed GET")
            return

        for line in lines[1:-1]:
            try:
                x, y, colour, message, pinned_str = line.split(
                    ",", 4)  # note the 5th field
                x = int(x)
                y = int(y)
                is_pinned = pinned_str.strip().lower() in (
                    "true", "1", "yes")  # convert to bool

                P1 = Point(x, y)
                P2 = Point(x + noteWidth, y + noteHeight)

                n = Note(colour, message, is_pinned, P1, P2, win, f"{x},{y}")
                n.draw()
                notes.append(n)
            except ValueError:
                print("Bad note line:", line)

        redraw_pins()

    # UI buttons
    clearButton = Button(Point(20, 20), Point(120, 60), "CLEAR", win).draw()
    disconnectButton = Button(Point(20, 80), Point(120, 120),
                              "DISCONNECT", win).setFontSize(8).draw()
    shakeButton = Button(Point(20, 140), Point(120, 180),
                         "SHAKE", win).draw()
    mode = "NOTE"
    toggleButton = Button(Point(20, 200), Point(120, 240),
                          f"Mode: {mode}", win).setFontSize(8).draw()

    redraw_board()

    while True:
        click = win.getMouse()

        if clearButton.clicked(click):
            client.sendall(b"CLEAR")
            client.recv(BUFFER)
            redraw_board()

        elif shakeButton.clicked(click):
            client.sendall(b"SHAKE")
            client.recv(BUFFER)
            redraw_board()
            for note in notes:
                if (not note.pinned):
                    note.undraw()

        elif disconnectButton.clicked(click):
            client.sendall(b"DISCONNECT")
            client.recv(BUFFER)
            win.close()
            return

        elif toggleButton.clicked(click):
            mode = "PIN" if mode == "NOTE" else "NOTE"
            toggleButton.setText(f"Mode: {mode}")

        elif mode == "NOTE":
            x = int(click.getX())
            y = int(click.getY())

            text = input("Enter note text: ")
            colour = input("Enter colour: ")

            client.sendall(f"POST {x} {y} {colour} {text}".encode())
            client.recv(BUFFER)
            redraw_board()

        elif mode == "PIN":
            temp = True
            x = int(click.getX())
            y = int(click.getY())

            for n in notes:
                if not n.clicked(click):
                    continue

                nx = int(n.p1.getX())
                ny = int(n.p1.getY())

                closest_pin = None
                best_dist = PIN_CLICK_RADIUS2

                for p in pins:
                    px = int(p.getCenter().getX())
                    py = int(p.getCenter().getY())

                    if nx <= px < nx + noteWidth and ny <= py < ny + noteHeight:
                        d = (px - x) ** 2 + (py - y) ** 2
                        if d < best_dist:
                            best_dist = d
                            closest_pin = (px, py)

                if closest_pin:
                    px, py = closest_pin
                    client.sendall(f"UNPIN {px} {py}".encode())
                    temp = False
                    n.pinned = False
                else:
                    client.sendall(f"PIN {x} {y}".encode())
                    temp = True
                    n.pinned = True

                client.recv(BUFFER)
                redraw_board()
                n.pinned = temp
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=DEF_HOST)
    parser.add_argument("--port", type=int, default=DEF_PORT)
    args = parser.parse_args()
    start_client(args.host, args.port)
