from time import sleep, time
import threading
import socket
import json

class ServerThread(threading.Thread):
    sockets = []
    host : str
    port : int 
    index : int

    def __init__(self, host, port) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.index = 0

    
    def new_server(self) -> None:
        self.server = socket.create_server((self.host, self.port))


    def add_connection(self):
        self.sockets.append(self.server.accept())
        print(f'Connection added:\nip: {self.sockets[self.index][1][0]}\tport: {self.sockets[self.index][1][1]}\n') 
        #self.index += 1

    def print_dict(self, data:str):
        dic = json.loads(data)
        for item in dic:
            print(f'{item}: \t{dic[item]}')
        print()
    

    def run(self):
        self.new_server()
        self.add_connection()
        while True:
            packet = self.sockets[self.index][0].recv(1024).decode('utf-8')
            self.print_dict(packet)
            