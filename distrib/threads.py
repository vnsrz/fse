from time import sleep, time
from room import Room
import threading
import socket
import json
import RPi.GPIO as GPIO

class RoomThread(threading.Thread):
    lights_timer : float
    recent_pres : bool

    def __init__(self, room: Room) -> None:
        super().__init__()
        self.room = room
    

    def run(self):
        self.recent_pres = False
        self.lights_timer = 0

        while True:
            self.room.count_ppl()
            self.room.print_temp()
            self.room.print_ppl()
            sleep(2)
            if self.room.alarm_on:
                # checks for activity
                if GPIO.input(self.room.inp['SPres']) or\
                    GPIO.input(self.room.inp['SPor']) or\
                    GPIO.input(self.room.inp['SJan']):
                    # activates the alarm
                    self.room.set_high('AL_BZ')
                else:
                    self.room.set_low('AL_BZ')
            
            else:
                # checks for activity
                if GPIO.input(self.room.inp['SPres']):
                    self.turn_lights_on()

                # checks for smoke
                if GPIO.input(self.room.inp['SFum']): 
                    self.room.set_high('AL_BZ')
                elif self.room.states['AL_BZ']: # turns buzzer off if already on
                    self.room.set_low('AL_BZ')
            
            if self.recent_pres:
                self.time_lights()
            sleep(0.1)


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

    def get_states(self) -> str:
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
        return json.dumps(dic)
    
    def get_ppl_qty(self) -> str:
        dic = {'Pessoas': self.room.ppl_qty}
        return json.dumps(dic)
    
    def get_temp_humd(self) -> str:
        dic = {'Temperatura' : self.room.temp, 'Umidade' : self.room.humd,}
        return json.dumps(dic)



class ConnectionThread(threading.Thread):
    def __init__(self, rt:RoomThread) -> None:
        super().__init__()
        self.room_thread = rt
        self.host = self.room_thread.room.central_address
        self.port = self.room_thread.room.central_port
    
    def create_con(self):
        self.central_soc = socket.create_connection((self.host, self.port))

    def send_message(self, message):
        self.central_soc.send(bytes(message, encoding='utf-8'))

    def run(self):
        self.create_con()
        self.room_thread.start()

        while True:
            states = self.room_thread.get_states()
            self.send_message(states)
            print('states sent')

            people_count = self.room_thread.get_ppl_qty()
            self.send_message(people_count)
            print('people count sent')

            temp_humd = self.room_thread.get_temp_humd()
            self.send_message(temp_humd)
            print('temp and humd sent')

            sleep(2)

