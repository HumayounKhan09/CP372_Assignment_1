"""
Server side note class 
"""

class note:
    def __init__(self,x:int,y:int,message:str,colour:str,pin_count:int=0):
        self.x = x
        self.y = y
        self.messages = message
        self.colour = colour
        self.pin_count = pin_count
        self.pins = set() #set of pin coordinates.
    
    def __str__(self):
        return f"{self.x},{self.y},{self.colour},{self.messages}"
    
    def is_pinned(self):
        return self.pin_count > 0
    
    def add_pin(self,x:int,y:int):
        self.pin_count += 1
        self.pins.add((x,y))

    def remove_pin(self,x:int,y:int):
        if (x,y) in self.pins:
            self.pin_count -= 1
            self.pins.remove((x,y))


