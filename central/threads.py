from time import sleep, time
import threading
import socket
import json

class ServerConnectionThread(threading.Thread):
    sockets: dict

    def __init__(self, host:str, port:int) -> None:
        super().__init__()
        self.sockets = {}
        self.server = socket.create_server((host, port))
    

    def run(self):
        sock, addr = self.server.accept()
        room = sock.recv(1024).decode('utf-8')
        self.sockets[room] = sock
        print(f'Connection added:\nname: {room}\t host: {addr[0]}\t port: {addr[1]}\n') 
    

class ServerThread(threading.Thread):
    sockets: dict

    def __init__(self, con: ServerConnectionThread) -> None:
        super().__init__()


    def print_dict(self, data:str):
        dic = json.loads(data)
        for item in dic:
            if item == 'Placa':
                print(f'{item}: \t\t{dic[item]}')
            else:
                print(f'{item}: \t{dic[item]}')
        print()
    

    def send_request(self, destiny):
        self.sockets[destiny].send(b'hammer it falco')


    def run(self):
        while True:
            destiny = 'Sala 02'
            self.send_request(destiny)
            packet = self.sockets[destiny].recv(4096).decode('utf-8')
            self.print_dict(packet)
            sleep(2)



        