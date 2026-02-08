from readerwriterlock import *
from server.note import note

class board_handler:
    def __init__(self,board_width:int,board_height:int,note_width:int,note_height:int,colours:list[str]):
        self.board_width = board_width
        self.board_height = board_height
        self.note_width = note_width
        self.note_height = note_height
        self.reader = rwlock.RWLockRead()
        self.writer = rwlock.RWLockWrite()
        self.colours = set(colours) #This needs to be a set for easy checks. 
        self.posted_notes= {} #key is going to be x, y coordinates, value is note object.
        self.pins = {}

    ###########################INTERNAL HELPERS############################
    def _is_notNegative(self,value:int):
        return value >= 0
    
    def _point_valid(self,x:int,y:int):
        return self._is_notNegative(x) and self._is_notNegative(y) and 0<= x <= self.board_width and 0<= y <= self.board_height
    
    def _note_within_bounds(self,x:int,y:int):
        return self._point_valid(x,y) and self._point_valid(x+self.note_width,y+self.note_height)
    
    
    def _inside_note(self, n: note, px: int, py: int):
        return (n.x <= px < n.x + self.note_width) and (n.y <= py < n.y + self.note_height)
    
    def _note_contains_point(self, x:int, y:int):
        affects = []
        for k, v in self.posted_notes.items():
            if self._inside_note(v,x,y):
                affects.append(k)
        return affects
    
    #######################Error Helpers########################
    def _err(self, err_code:str):
        return f"ERROR {err_code}"
    def _ok(self, message:str):
        return f"OK {message}"
    
    def _ok_lst(self, lines:list[str]):
        out = ["OK"]
        out.extend(lines)
        out.append("END")
        return "\n".join(out)
    
    ############################COMMANDS############################
    
    def POST(self,x:int,y:int,colour:str,message:str): 
        #writiing the validation code:
        if not self._note_within_bounds(x,y):
            return self._err("OUT_OF_BOUNDS")
        if colour not in self.colours:
            return self._err("INVALID_COLOUR")
        if (x,y) in self.posted_notes:
            return self._err("COMPLETE_OVERLAP")
        message = (message or "").replace("\n", " ").replace("\r", " ").strip()
        self.posted_notes[(x,y)] = note(x,y,message,colour)
        return self._ok("NOTE_POSTED")

    def PIN(self,x:int,y:int):
        with self.writer.gen_wlock():
            if not self._point_valid(x,y):
                return self._err("OUT_OF_BOUNDS")
            affects = self._note_contains_point(x,y)
            if len(affects) == 0:
                return self._err("NO_NOTE")
            pin = (x,y)
            if pin not in self.pins:
                self.pins[pin] = set()

            for note in affects:
                n = self.posted_notes[(note.x,note.y)]
                n.add_pin(x,y)
                self.pins[pin].add(n)
            return self._ok("NOTE_PINNED")
        
    def UNPIN(self, x:int, y:int):
        with self.writer.gen_wlock():
            if not self._point_valid(x,y):
             return self._err("OUT_OF_BOUNDS")
            pin = (x,y)
            if pin not in self.pins:
                return self._err("PIN_NOT_FOUND")
            
            for n in list(self.pins[pin]):
                if n in self.posted_notes:
                    self.posted_notes[n].remove_pin(x,y)
            del self.pins[pin]
            return self._ok(f"UNPINNED_({x},{y})")

    def SHAKE(self):
        with self.writer.gen_wlock():
            to_rm= [nk for nk, n in self.posted_notes.items() if not n.is_pinned()]
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
            lines = [f"PIN {x}{y}" for (x,y) in coord]
            return self._ok_lst(lines)
    def GET(self, colour=None, contains=None, refersTo= None):
        with self.reader.gen_rlock():
            if colour is not None and colour not in self.colours:
                return self._err("COLOUR_NOT_SUPPORTED")
            
            if contains is not None:
                x,y = contains
                if not self._is_notNegative(x) and self._is_notNegative(y):
                    return self._err("INVALID_FORMAT")
                
                if not self._point_valid(x,y):
                    return self._err("OUT_OF_BOUNDS")
                
            if refersTo is not None: 
                refersTo = refersTo.strip()
                
            output = []
            for n in self.posted_notes.values():
                if colour is not None and n.colour != colour:
                    continue
                if contains is not None:
                    x,y = contains
                    if not self._inside_note(n,x,y):
                        continue
                if refersTo is not None and refersTo not in n.messages:
                    continue
                output.append(n)
            output.sort(key=lambda t: (t.y, t.x, t.colour, t.messages))
            return self._ok_lst([str(n) for n in output])









