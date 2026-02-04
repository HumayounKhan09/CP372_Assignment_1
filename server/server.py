"""
This file implements the  server, which is mutlithreaded
"""

#Spin up a server
import socket
from _thread import start_new_thread
import argparse
import sys
import json

DEF_HOST = ''
DEF_PORT = 9000
BUFFER = 1024
BACKLOG = 10
DEF_COLOUR_SCHEME = 'gold purple'




def server_ops(client_socket: socket.socket, client_address: tuple, board_width: int, board_height:int, note_width:int, note_height: int, colours:str) -> None:
    client_ip, client_port = client_address
    #When a client first connects, send handshake data:
    #handshake data set up when the server initializes. 
    data_to_send = [board_width,board_height,note_height,note_width,colours]
    message = json.dumps(data_to_send).encode('utf-8') 
    client_socket.sendall(message)

    
    
            

def main(host: str,port:int, board_width: int, board_height:int, note_width:int, note_height: int, colours:str):
    #Setting up the server: 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Allow reusing the socket address immediately
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind and listen
        server_socket.bind((host, port))
        server_socket.listen(BACKLOG)

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                start_new_thread (server_ops, (client_socket,client_address,board_width,board_height,note_width,note_height,colours))

            except:
                break
    except OSError:
        sys.exit(1)

    finally:
        server_socket.close()
        #Powers down the server.

#Args are set by the setup command, then passed to eacb subsequent thread

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #host
    parser.add_argument("host", default = DEF_HOST)
    #port number
    parser.add_argument("port",type =int)
    #Board Width
    parser.add_argument("board_width",type= int)
    #board height
    parser.add_argument("board_height", type = int)
    #note width
    parser.add_argument("note_width", type = int)
    #note height
    parser.add_argument("note_height", type= int)
    #colours
    parser.add_argument("colours", type = str)

    args = parser.parse_args()
    main(args.host, args.port, args.board_height, args.board_width, args.note_width, args.note_height, args.colours)



    


 