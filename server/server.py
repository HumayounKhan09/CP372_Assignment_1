"""
This file implements the  server, which is mutlithreaded
"""

# Spin up a server
import socket
from _thread import start_new_thread
from typing import List
import argparse
import sys
import json
from readerwriterlock import *
from note import note

DEF_HOST = '0.0.0.0'
DEF_PORT = 5000
BUFFER = 1024
BACKLOG = 10
DEF_COLOUR_SCHEME = ['gold', 'purple']


class board_handler:
    def __init__(self, board_width: int, board_height: int, note_width: int, note_height: int, colours: list[str]):
        self.board_width = board_width
        self.board_height = board_height
        self.note_width = note_width
        self.note_height = note_height
        self.reader = rwlock.RWLockRead()
        self.writer = rwlock.RWLockWrite()
        self.colours = set(colours)
        self.posted_notes = {}
        self.pins = {}

    ########################### INTERNAL HELPERS############################
    def _is_notNegative(self, value: int):
        return value >= 0

    def _point_valid(self, x: int, y: int):
        return self._is_notNegative(x) and self._is_notNegative(y) and 0 <= x <= self.board_width and 0 <= y <= self.board_height

    def _note_within_bounds(self, x: int, y: int):
        return self._point_valid(x, y) and self._point_valid(x+self.note_width, y+self.note_height)

    def _inside_note(self, n: note, px: int, py: int):
        return (n.x <= px < n.x + self.note_width) and (n.y <= py < n.y + self.note_height)

    def _note_contains_point(self, x: int, y: int):
        affects = []
        for k, v in self.posted_notes.items():
            if self._inside_note(v, x, y):
                affects.append(k)
        return affects

    ####################### Error Helpers########################
    def _err(self, err_code: str):
        return f"ERROR {err_code}"

    def _ok(self, message: str):
        return f"OK {message}"

    def _ok_lst(self, lines: list[str]):
        out = ["OK"]
        out.extend(lines)
        out.append("END")
        return "\n".join(out)

    ############################ COMMANDS############################

    def POST(self, x: int, y: int, colour: str, message: str):
        # writiing the validation code:
        if not self._note_within_bounds(x, y):
            return self._err("OUT_OF_BOUNDS")
        if colour not in self.colours:
            return self._err("INVALID_COLOUR")
        if (x, y) in self.posted_notes:
            return self._err("COMPLETE_OVERLAP")
        message = (message or "").replace("\n", " ").replace("\r", " ").strip()
        self.posted_notes[(x, y)] = note(x, y, message, colour)
        return self._ok("NOTE_POSTED")

    def PIN(self, x: int, y: int):
        with self.writer.gen_wlock():
            if not self._point_valid(x, y):
                return self._err("OUT_OF_BOUNDS")

            affects = self._note_contains_point(x, y)
            if not affects:
                return self._err("NO_NOTE")

            pin = (x, y)
            if pin not in self.pins:
                self.pins[pin] = set()

            for note_key in affects:
                n = self.posted_notes[note_key]
                n.add_pin(x, y)
                self.pins[pin].add(n)

            return self._ok("NOTE_PINNED")

    def UNPIN(self, x: int, y: int):
        with self.writer.gen_wlock():
            if not self._point_valid(x, y):
                return self._err("OUT_OF_BOUNDS")
            pin = (x, y)
            if pin not in self.pins:
                return self._err("PIN_NOT_FOUND")

            for n in list(self.pins[pin]):
                if n in self.posted_notes:
                    self.posted_notes[n].remove_pin(x, y)
            del self.pins[pin]
            return self._ok(f"UNPINNED_({x},{y})")

    def SHAKE(self):
        with self.writer.gen_wlock():
            to_rm = [nk for nk, n in self.posted_notes.items()
                     if not n.is_pinned()]
            for n in to_rm:
                del self.posted_notes[n]
            return self._ok("SHAKE_COMPLETE")

    def CLEAR(self):
        with self.writer.gen_wlock():
            self.posted_notes.clear()
            self.pins.clear()
            return self._ok("CLEAR_COMPLETE")

    def GET_PINS(self):
        with self.reader.gen_rlock():
            coord = sorted(self.pins.keys())
            lines = [f"PIN {x} {y}" for (x, y) in coord]
            return self._ok_lst(lines)

    def GET(self, colour: str = "None", contains: str = "None", refersTo: str = "None"):
        with self.reader.gen_rlock():
            if colour != "None" and colour not in self.colours:
                return self._err("COLOUR_NOT_SUPPORTED")

            if contains != "None":
                x, y = contains

                if not self._point_valid(int(x), int(y)):
                    return self._err("OUT_OF_BOUNDS")

            if refersTo != "None":
                refersTo = refersTo.strip()

            output = []
            for n in self.posted_notes.values():
                if colour != "None" and n.colour != colour:
                    continue
                if contains != "None":
                    x, y = contains
                    if not self._inside_note(n, int(x), int(y)):
                        continue
                if refersTo != "None" and refersTo not in n.messages:
                    continue
                output.append(n)
            output.sort(key=lambda t: (t.y, t.x, t.colour, t.messages))
            print(output)
            return self._ok_lst([str(n) for n in output])


def server_ops(client_socket: socket.socket, client_address: tuple,
               board_width: int, board_height: int,
               note_width: int, note_height: int, colours: list[str]) -> None:

    client_ip, client_port = client_address
    print(f"Connection from {client_ip}:{client_port}")

    # Send handshake
    data_to_send = [board_width, board_height,
                    note_height, note_width, colours]
    client_socket.sendall(json.dumps(data_to_send).encode('utf-8'))

    board = board_handler(board_width, board_height,
                          note_width, note_height, colours)

    try:
        while True:
            data = client_socket.recv(BUFFER)
            if not data:
                break

            command = data.decode('utf-8').strip()
            response = handle_command(board, command)
            client_socket.sendall(response.encode('utf-8'))

    except ConnectionResetError:
        print(f"Connection lost from {client_ip}:{client_port}")
    finally:
        client_socket.close()


def handle_command(board: board_handler, command_str: str) -> str:
    parts = command_str.strip().split()
    if not parts:
        return "ERROR EMPTY_COMMAND"

    cmd = parts[0].upper()

    try:
        if cmd == "POST":
            x, y = int(parts[1]), int(parts[2])
            colour = parts[3]
            message = " ".join(parts[4:]) if len(parts) > 4 else ""
            return board.POST(x, y, colour, message)

        elif cmd == "PIN":
            x, y = int(parts[1]), int(parts[2])
            return board.PIN(x, y)

        elif cmd == "UNPIN":
            x, y = int(parts[1]), int(parts[2])
            return board.UNPIN(x, y)

        elif cmd == "SHAKE":
            return board.SHAKE()

        elif cmd == "CLEAR":
            return board.CLEAR()

        elif cmd == "GET_PINS":
            return board.GET_PINS()

        elif cmd == "GET":
            # Expected format:
            # GET <colour|None> <x|None> <y|None> <refersTo|None>

            if len(parts) != 5:
                return "ERROR INVALID_FORMAT"

            colour = parts[1]
            x = parts[2]
            y = parts[3]
            refersTo = parts[4]

            if x == "None" and y == "None":
                contains = "None"
            else:
                contains = (x, y)

            return board.GET(colour, contains, refersTo)

        else:
            return "ERROR UNKNOWN_COMMAND"

    except (IndexError, ValueError):
        return "ERROR INVALID_FORMAT"


def main(host: str, port: int, board_width: int, board_height: int, note_width: int, note_height: int, colours: str):
    print("hi")
    # Setting up the server:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind and listen
        server_socket.bind((host, port))
        server_socket.listen(BACKLOG)
        print("Waiting for a connection...")

        while True:
            try:
                print("Waiting for a connection...")
                client_socket, client_address = server_socket.accept()
                start_new_thread(server_ops, (client_socket, client_address,
                                 board_width, board_height, note_width, note_height, colours))

            except:
                break
    except OSError:
        sys.exit(1)

    finally:
        server_socket.close()
        # Powers down the server.

# Args are set by the setup command, then passed to eacb subsequent thread


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # host
    parser.add_argument("host", default=DEF_HOST)
    # port number
    parser.add_argument("port", type=int)
    # Board Width
    parser.add_argument("board_width", type=int)
    # board height
    parser.add_argument("board_height", type=int)
    # note width
    parser.add_argument("note_width", type=int)
    # note height
    parser.add_argument("note_height", type=int)
    # colours
    parser.add_argument("colours", nargs="+")

    args = parser.parse_args()
    main(args.host, args.port, args.board_width, args.board_height,
         args.note_width, args.note_height, args.colours)
