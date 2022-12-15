from time import sleep, time
from room import Room
import threading
import socket
# import RPi.GPIO as GPIO

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
            # if self.room.alarm_on:
            #     # checks for activity
            #     if GPIO.input(self.room.inp['SPres']) or\
            #         GPIO.input(self.room.inp['SPor']) or\
            #         GPIO.input(self.room.inp['SJan']):
            #         # activates the alarm
            #         self.room.set_high('AL_BZ')
            #     else:
            #         self.room.set_low('AL_BZ')
            
            # else:
            #     # checks for activity
            #     if GPIO.input(self.room.inp['SPres']):
            #         self.turn_lights_on()

            #     # checks for smoke
            #     if GPIO.input(self.room.inp['SFum']): 
            #         self.room.set_high('AL_BZ')
            #     elif self.room.state['AL_BZ']: # turns buzzer off if already on
            #         self.room.set_low('AL_BZ')
            
            # if self.recent_pres:
            #     self.time_lights()
            # sleep(0.1)


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

class ConnectionThread(threading.Thread):
    def __init__(self, rt:RoomThread, host, port) -> None:
        super().__init__()
        self.room_thread = rt
        self.host = host
        self.port = port
    
    def create_con(self):
        self.central_soc = socket.create_connection((self.host, self.port))

    def run(self):
        self.create_con()
        self.rt.start()
        self.central_soc.send("eco")

