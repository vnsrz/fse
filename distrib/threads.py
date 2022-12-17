from time import sleep, time
from room import Room
import threading
import socket
import json
import sys
import RPi.GPIO as GPIO

class RoomThread(threading.Thread):
    lights_timer : float
    recent_pres : bool

    def __init__(self, room: Room) -> None:
        super().__init__()
        self.room = room
    

    def turn_lights_on(self):
        self.room.set_high('L_01')
        self.room.set_high('L_02')
        self.lights_timer = time()
        self.recent_pres = True


    def time_lights(self):
        if time() - self.lights_timer > 15.0:
            self.room.set_low('L_01')
            self.room.set_low('L_02')
            self.lights_timer = None
            self.recent_pres = False


    def get_states(self) -> dict:
        dic = {}

        for item in self.room.states:
            if item == 'L_01':
                dic['Lâmpada 01'] = self.room.states['L_01']
            elif item == 'L_02':
                dic['Lâmpada 02'] = self.room.states['L_02']
            elif item == 'PR':
                dic['Projetor'] = self.room.states['PR']
            elif item == 'AC':
                dic['Ar-Con'] = self.room.states['AC']
            elif item == 'AL_BZ':
                dic['Sirene'] = self.room.states['AL_BZ']
        return dic


    def check_sensors(self) -> bool:
        for sensor in self.room.sensors:
            return GPIO.input(self.room.inp[sensor])
    
    def get_sensors(self) -> dict:
        dic = {}

        for sensor in self.room.sensors:
            if sensor == 'SPres':
                name = 'S. Presença'
            elif sensor == 'SFum':
                name = 'S. Fumaça'
            elif sensor == 'SJan':
                name = 'S. Janela'
            elif sensor == 'SPor':
                name = 'S. Porta'

            if GPIO.input(self.room.inp[sensor]):
                dic[name] = 'Ligado'
            else:
                dic[name] = 'Desligado'
        return dic


    def get_ppl_qty(self) -> dict:
        dic = {'Pessoas': self.room.ppl_qty}
        return dic
    

    def get_temp_humd(self) -> dict:
        dic = {'Temperatura' : self.room.temp, 'Umidade' : self.room.humd,}
        return dic
    
    
    def get_json_dump(self) -> str:
        dic = {'Placa' : self.room.name}
        dic = dic | self.get_states() | self.get_ppl_qty() | self.get_temp_humd() | self.get_sensors()
        return json.dumps(dic)


    def run(self):
        self.recent_pres = False
        self.lights_timer = 0

        while True:
            self.room.count_ppl()
            self.room.check_temp()
            if self.check_sensors():
                if self.room.alarm_on:
                    self.room.set_high('AL_BZ')
                else:
                    if GPIO.input(self.room.inp['SPres']):
                        self.turn_lights_on()

                    if GPIO.input(self.room.inp['SFum']): 
                        self.room.set_high('AL_BZ')

                    elif self.room.states['AL_BZ']: # turns buzzer off if already on
                        self.room.set_low('AL_BZ')
            
            if self.recent_pres:
                self.time_lights()
            sleep(0.1)

        
class ConnectionThread(threading.Thread):
    def __init__(self, room:Room) -> None:
        super().__init__()
        self.room_thread = RoomThread(room)
        self.room_thread.daemon = True
        self.host = self.room_thread.room.central_address
        self.port = self.room_thread.room.central_port
    

    def create_con(self):
        self.central_soc = socket.create_connection((self.host, self.port))
        self.send_message(self.room_thread.room.name)
        print(f'connected to {self.host}')


    def send_message(self, message):
        self.central_soc.send(bytes(message, encoding='utf-8'))
    

    def run(self):
        self.create_con()
        self.room_thread.start()
        print()
        while True:
            print('standing by...')
            request = self.central_soc.recv(1024).decode('utf-8')

            if request == 'kys NOW':
                print('server down')
                sys.exit()

            elif request == 'hammer it falco':
                message = self.room_thread.get_json_dump()
                self.send_message(message)
                print('data sent')
            
            elif request == 'L_ON':
                self.room_thread.room.set_high('L_01')
                self.room_thread.room.set_high('L_02')
                self.send_message('success')
                print('all lights are on')

            elif request == 'L_OFF':
                self.room_thread.room.set_low('L_01')
                self.room_thread.room.set_low('L_02')
                self.send_message('success')
                print('all lights are off')

            elif request == 'AC' or request == 'PR' or request == 'L_01' or request == 'L_02':
                self.room_thread.room.switch(request)
                self.send_message('success')
                print(f'{request} switched')

            elif request == 'all_off':
                self.room_thread.room.all_off()
                self.send_message('success')
                print('all outputs are off')

            elif request == 'switch_alarm':
                if self.room_thread.room.alarm_on: 
                    self.room_thread.room.alarm_on = False
                    self.send_message('success')
                elif self.room_thread.check_sensors:
                    self.send_message('há sensores ativos, alarme não pode ser acionado')
                    print('alarme não acionado')
                else:
                    self.room_thread.room.alarm_on = True
                    self.send_message('success')
                    print('alarme acionado')

