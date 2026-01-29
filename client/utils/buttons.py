from client.utils.graphics import Point
from graphics import Button, GraphWin


class DisconnectButton(Button):
    def __init__(self, p1: Point, p2: Point, text: str, win, client):
        super().__init__(p1, p2, text, win)

    def disconnect(self):
        pass  # gracefully disconnect from the server


class ClearButton(Button):
    def __init__(self, p1: Point, p2: Point, text: str, win):
        super().__init__(p1, p2, text, win)

    def clear(self):
        pass  # should send a message to clear the board
