
from client.utils.coordinates import coordinates
from graphics import *


class Pin(Circle):
    def __init__(self, center: Point, radius: int):
        super().__init__(center, radius)


"""
Usage: pin = Pin(Point(x1, y1),  5)
"""
