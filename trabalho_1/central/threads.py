from datetime import datetime
from time import sleep
import threading
import socket
import json
import sys
import os

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

class ServerThread(threading.Thread):
    sockets: dict

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.sockets = {}
        self.server = socket.create_server((host, port))


    def run(self) -> None:
        while True:
            sock, addr = self.server.accept()
            room = sock.recv(1024).decode('utf-8')
            self.sockets[room] = sock


class StatesThread(threading.Thread):
    states: dict
    sockets: dict

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.server = ServerThread(host, port)
        self.server.daemon = True
        self.states = {}
        self.sockets = {}
    

    def send_request(self, destiny, message) -> None:
        self.sockets[destiny].send(bytes(message, encoding='utf-8'))


    def run(self) -> None:
        self.server.start()
        while True:
            self.sockets = self.server.sockets
            for board in self.sockets:
                self.send_request(board, 'update')
                self.states[board] = json.loads(self.sockets[board].recv(4096).decode('utf-8'))
            sleep(2)


class ConsoleThread(threading.Thread):
    sockets: dict
    alarm: bool
    global_count: int

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.st = StatesThread(host, port)
        self.st.daemon = True
        self.alarm = False
        self.sockets = {}
        self.global_count = 0
    

    def send_request(self, destiny, message) -> None:
        self.sockets[destiny].send(bytes(message, encoding='utf-8'))
    

    def wait_response(self, board) -> str:
        response = self.sockets[board].recv(4096).decode('utf-8')
        print(response)
        return response


    def print_dict(self, dic:dict) -> None:
        print()
        for item in dic:
            if item == 'Placa':
                print(f'{item}: \t\t{dic[item]}')
            else:
                print(f'{item}: \t{dic[item]}')


    def print_boards(self, sockets) -> None:
        print(ROOMS)
        for board in sockets:
            print(board)
        print(CONSOLE)


    def cls(self) -> None:
        os.system('clear')


    def update_states(self, board) -> None:
        self.send_request(board, 'update')
        self.st.states[board] = json.loads(self.sockets[board].recv(4096).decode('utf-8'))

    
    def check_sensors(self, board) -> bool:
        dic = self.st.states[board]

        if dic['S. Presença'] == 'Ligado' or\
        dic['S. Fumaça'] == 'Ligado' or\
        dic['S. Janela'] == 'Ligado' or\
        dic['S. Porta'] == 'Ligado':
            return True
        else: return False


    def lights_console(self, board) -> str:
        self.cls()
        self.print_dict(self.st.states[board])
        choice = input(LIGHTS)

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
            self.print_dict(self.st.states[board])
            choice = input(CONSOLE_ROOM)

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
                self.update_states(board)

    
    def print_ppl_count(self, sockets) -> None:
        self.global_count = 0
        for board in sockets:
            self.global_count += int(self.st.states[board]['Pessoas'])
        print(f'Qtd de pessoas no prédio: {self.global_count}\n')


    def write_log(self, event:str) -> None:
        with open('log.csv', 'a', encoding='UTF8') as f:
            f.write(f'{event},{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')


    def run(self):
        self.st.start()
        log = f'central,servidor iniciado'
        self.write_log(log)
        self.cls()
        while True:
            self.sockets = self.st.sockets
            if self.sockets:
                for board in self.sockets:
                    self.update_states(board)

                self.print_boards(self.sockets)
                if self.alarm: print('Estado do alarme: Ligado') 
                else:print('Estado do alarme: Desligado')
                self.print_ppl_count(self.sockets)

                choice = input()

                if choice == '0': # exit
                    for board in self.sockets:
                        self.send_request(board, 'kys NOW')
                    log = f'central,servidor terminado'
                    self.write_log(log)
                    sys.exit()
                elif choice == '1': # activate alarm
                    for board in self.sockets:
                        if self.check_sensors(board):
                            self.cls()
                            print('há sensores ativos, alarme não pode ser acionado')
                        else:
                            self.send_request(board, 'switch_alarm')
                            self.cls()
                            self.wait_response(board)
                    if self.st.states:
                        if self.alarm:
                            self.alarm = False
                            log = f'central,sistema de alarme desligado'
                            self.write_log(log)
                        else: 
                            self.alarm = True
                            log = f'central,sistema de alarme ligado'
                            self.write_log(log)
                elif choice == '2': # all lights on
                    for board in self.sockets:
                        self.send_request(board, 'L_ON')
                        self.cls()
                        self.wait_response(board)
                        log = f'{board},luzes acionadas'
                        self.write_log(log)
                elif choice == '3': # all charges off
                    for board in self.sockets:
                        self.send_request(board, 'all_off')
                        self.cls()
                        self.wait_response(board)
                        log = f'{board},cargas desligadas'
                        self.write_log(log)
                else: 
                    self.cls()
                    for board in self.sockets:
                        if choice == board:
                            self.room_console(board)

