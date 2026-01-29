from graphics import *
from clientServer import Client

# Open the window
win = GraphWin("CP372 - A01", 500, 500)


# Define the Client's connection to the Server
client = Client()

# Define the GUI
clearButton = Button(Point(20, 20), Point(100, 60), "CLEAR", win).draw()
disconnectButton = Button(
    Point(20, 80), Point(100, 120), "DISCONNECT", win).setFontSize(8).draw()


# Define the input
portEntry = Entry(Point(450, 20), 10).draw(win)
ipEntry = Entry(Point(450, 40), 10).draw(win)

while True:
    pt = win.getMouse()
    if (clearButton.clicked(pt)):
        print("Clear")
        client.clear()  # the code to handle the clear input
        pass
    elif (disconnectButton.clicked(pt)):
        print("Disconnect")
        client.disconnect()  # the code to handle the disconnect
        pass
