from time import sleep, time
from threading import Thread
import socket
import json
import sys
import os

class ServerThread(Thread):
    sockets: dict

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.sockets = {}
        self.server = socket.create_server((host, port))


    def run(self):
        while True:
            sock, addr = self.server.accept()
            room = sock.recv(1024).decode('utf-8')
            self.sockets[room] = sock
            #print(f'\nConnection added: {room}\t host: {addr[0]}\t port: {addr[1]}\n')


class ServerRecvThread(Thread):
    ROOMS ="""
---------Salas Conectadas--------
"""
    CONSOLE ="""
--------Painel de Controle-------
Digite o nome da sala para checar seus estados

    [1] Atualizar lista de salas
    [0] Sair do programa
"""
    CONSOLE_ROOM ="""
--------Painel de Controle-------
Aperte Enter para atualizar estados

    [1] Acionar as lâmpadas
    [2] Acionar o ar-condicionado
    [3] Acionar o projetor
    [4] Desligar tudo
    [0] Retornar

"""
    LIGHTS ="""
---------Acionar Lâmpadas---------
Aperte Enter para atualizar estados

    [1] Lâmpada 1
    [2] Lâmpada 2
    [3] Ligar todas
    [4] Desligar todas
    [0] Retornar

"""
    states: dict
    sockets: dict
    # stop_threads: bool


    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.server = ServerThread(host, port)
        self.server.daemon = True
        self.states = {}
        self.sockets = {}
        # self.stop_threads = False
    

    def send_request(self, destiny, message) -> None:
        self.sockets[destiny].send(bytes(message, encoding='utf-8'))
    

    def wait_response(self, board) -> None:
        response = self.sockets[board].recv(4096).decode('utf-8')
        print(response)


    def print_dict(self, data:str) -> None:
        dic = json.loads(data)
        print()
        for item in dic:
            if item == 'Placa':
                print(f'{item}: \t\t{dic[item]}')
            else:
                print(f'{item}: \t{dic[item]}')


    def print_boards(self, states) -> None:
        print(self.ROOMS)
        for board in states:
            print(board)
        print(self.CONSOLE)


    # def clear_scr(self, n) -> None:
    #     for _ in range(n):
    #         print()
    

    def cls(self):
        os.system('clear')


    def print_states(self, board) -> None:
        self.send_request(board, 'hammer it falco')
        self.states[board] = self.sockets[board].recv(4096).decode('utf-8')
        self.print_dict(self.states[board])


    def lights_console(self, board) -> str:
        self.cls()
        self.print_states(board)
        choice = input(self.LIGHTS)

        if choice == '0': return ''
        elif choice == '1': return 'L_01'
        elif choice == '2': return 'L_02'
        elif choice == '3': return 'L_ON'
        elif choice == '4': return 'L_OFF'

    def room_console(self, board) -> None:
        while True:
            self.print_states(board)
            choice = input(self.CONSOLE_ROOM)

            if(choice == '0'):
                self.cls()
                return
            elif choice == '1': msg = self.lights_console(board)
            elif choice == '2': msg = 'AC'
            elif choice == '3': msg = 'PR'
            elif choice == '4': msg = 'all_off'
            if choice == '': pass
            else:
                self.send_request(board, msg)
                self.cls()
                self.wait_response(board)
            
    

    # def update_console(self, board, msg):
    #     while True:
    #         if self.stop_threads: break
    #         self.cls()
    #         self.print_states(board)
    #         print(msg)
    #         sleep(2)
    

    def run(self):
        self.server.start()

        while True:
            self.sockets = self.server.sockets
            if self.sockets:
                self.print_boards(self.sockets)
                choice = input()
                if choice == '0':
                    for board in self.sockets:
                        self.send_request(board, 'kys NOW')
                    sys.exit()
                else:
                    self.cls()
                    for board in self.sockets:
                        if choice == board:
                            self.room_console(board)