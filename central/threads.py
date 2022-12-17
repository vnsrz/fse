from time import sleep, time
from threading import Thread
from datetime import datetime
import socket
import csv
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
Aperte Enter para atualizar a lista de salas
Digite o nome da sala para checar seus estados

    [1] Acionar o alarme
    [2] Ligar todas as lâmpadas do prédio
    [3] Desligar todas as cargas do prédio
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
    alarm: bool

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.server = ServerThread(host, port)
        self.server.daemon = True
        self.states = {}
        self.sockets = {}
        self.alarm = False
    

    def send_request(self, destiny, message) -> None:
        self.sockets[destiny].send(bytes(message, encoding='utf-8'))
    

    def wait_response(self, board) -> str:
        response = self.sockets[board].recv(4096).decode('utf-8')
        print(response)
        return response


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
        elif choice == '1':
            msg = 'L_01'
            log = f'{board},{msg} acionado'
            self.write_log(log)
            return msg
        elif choice == '2':
            msg = 'L_02'
            log = f'{board},{msg} acionado'
            self.write_log(log)
            return msg
        elif choice == '3':
            msg = 'L_ON'
            log = f'{board},lampadas ligadas'
            self.write_log(log)
            return msg
        elif choice == '4':
            msg = 'L_OFF'
            log = f'{board},lampadas desligadas'
            self.write_log(log)
            return msg

    def room_console(self, board) -> None:
        while True:
            self.print_states(board)
            choice = input(self.CONSOLE_ROOM)

            if(choice == '0'):
                self.cls()
                return
            elif choice == '1': msg = self.lights_console(board)
            elif choice == '2':
                msg = 'AC'
                log = f'{board},{msg} acionado'
                self.write_log(log)
            elif choice == '3': 
                msg = 'PR'
                log = f'{board},{msg} acionado'
                self.write_log(log)
            elif choice == '4':
                msg = 'all_off'
                log = f'{board},tudo desligado'
                self.write_log(log)
            if choice == '': self.cls()
            else:
                self.send_request(board, msg)
                self.cls()
                self.wait_response(board)
            
    
    def write_log(self, event:str):
        with open('log.csv', 'a', encoding='UTF8') as f:
            f.write(f'{event},{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')
    

    def run(self):
        self.server.start()
        
        while True:
            self.sockets = self.server.sockets
            if self.sockets:
                self.print_boards(self.sockets)
                if self.alarm: print('Estado do alarme: Ligado\n') 
                else:print('Estado do alarme: Desligado\n')
                choice = input()

                if choice == '0': # exit
                    for board in self.sockets:
                        self.send_request(board, 'kys NOW')
                    sys.exit()
                elif choice == '1': # activate alarm
                    self.send_request(board, 'switch_alarm')
                    self.cls()
                    if self.wait_response(board) == 'sucess':
                        if self.alarm: self.alarm = False
                        else: self.alarm = True
                elif choice == '2': # all lights on
                    for board in self.sockets:
                        self.send_request(board, 'L_ON')
                        self.cls()
                        self.wait_response(board)
                elif choice == '3': # all charges off
                    for board in self.sockets:
                        self.send_request(board, 'all_off')
                        self.cls()
                        self.wait_response(board)
                else:
                    self.cls()
                    for board in self.sockets:
                        if choice == board:
                            self.room_console(board)
