from client.utils.coordinates import coordinates
from client.graphics import *
from pins import Pin
from typing import List
# GUI


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


"""
Usage: note = Note(color, message, is_pinned, Point(x1,y1), Point(x2,y2), win)
Extends Button so that when users click it unpins? 

When a user clicks on the Note self.clicked === TRUE
"""
