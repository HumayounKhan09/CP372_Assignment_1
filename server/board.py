from queue import Queue

class board_handler:
    def __init__(self,board_width,board_height,note_width,note_height,colours):
        self.board_width = board_width
        self.board_height = board_height
        self.note_width = note_width
        self.note_height = note_height
        self.colours = colours #This needs to be a set for easy checks. 
        self.posted_notes= {} #key is going to be x, y coordinates, value is the colour + message


    
    def POST(self):
        #only pinned notes appear on the board, with other notes appearing in the queue array. 
        
        pass

    def GET(self):
        pass

    def PIN(self):
        pass

    def UNPIN(self):
        pass

    def SHAKE(self):
        pass

    def CLEAR(self): 
        pass

    # you can confidently use this Queue for concurrency
    print(Queue().mutex)  # mutex is a lock (hover over it)
    # Queue uses the lock internally
