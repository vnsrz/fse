from time import sleep, time
import Adafruit_DHT as DHT
import RPi.GPIO as GPIO
import threading
import json

class Room:
    inp : dict
    out: dict
    state : dict
    ppl_qty : int
    temp : float
    humd : float
    alarm_on : bool

    def __init__(self, filename: str) -> None:
        with open(filename, 'r') as f:
            file = json.load(f)

        # reads the inputs and outputs from the json file
        json_inputs = file['inputs']
        json_outputs = file['outputs']
        
        # creates an empty dict for the inputs and outputs
        self.inp = {} 
        self.out = {} 

        for item in json_inputs:
            if item['tag'] == 'Sensor de Presença':
                self.inp['SPres'] = item['gpio']
            elif item['tag'] == 'Sensor de Fumaça':
                self.inp['SFum'] = item['gpio']
            elif item['tag'] == 'Sensor de Janela':
                self.inp['SJan'] = item['gpio']
            elif item['tag'] == 'Sensor de Porta':
                self.inp['SPor'] = item['gpio']
            elif item['tag'] == 'Sensor de Contagem de Pessoas Entrada':
                self.inp['SC_IN'] = item['gpio']
            elif item['tag'] == 'Sensor de Contagem de Pessoas Saída':
                self.inp['SC_OUT'] = item['gpio']

        for item in json_outputs:
            if item['tag'] == 'Lâmpada 01':
                self.out['L_01'] = item['gpio']
            elif item['tag'] == 'Lâmpada 02':
                self.out['L_02'] = item['gpio']
            elif item['tag'] == 'Projetor Multimidia':
                self.out['PR'] = item['gpio']
            elif item['tag'] == 'Ar-Condicionado (1º Andar)':
                self.out['AC'] = item['gpio']
            elif item['tag'] == 'Sirene do Alarme':
                self.out['AL_BZ'] = item['gpio']
        
        # creates a dict through dict comprehension to store the state of all outputs
        self.state = {k: False for k in self.out}
        self.dht22 = file['sensor_temperatura'][0]['gpio']
        self.ppl_qty = 0
        self.alarm_on = False

        # sets up the board
        GPIO.setmode(GPIO.BCM)
        for pin in self.out.values():
            GPIO.setup(pin, GPIO.OUT)

        for pin in self.inp.values():
            GPIO.setup(pin, GPIO.IN)
        
        GPIO.add_event_detect(self.inp['SC_IN'], GPIO.RISING)
        GPIO.add_event_detect(self.inp['SC_OUT'], GPIO.RISING)

        self.turn_off()
    

    def turn_off(self) -> None:
        for pin in self.out:
            self.set_low(pin)
    

    def set_high(self, pin:str) -> None:
        GPIO.output(self.out[pin], GPIO.HIGH)
        self.state[pin] = True


    def set_low(self, pin:str) -> None:
        GPIO.output(self.out[pin], GPIO.LOW)
        self.state[pin] = False


    def count_ppl(self) -> None:
        if GPIO.event_detected(self.inp['SC_IN']):
            self.ppl_qty += 1
        if GPIO.event_detected(self.inp['SC_OUT']) and self.ppl_qty > 0:
            self.ppl_qty -= 1


    def check_temp(self) -> None:
        self.temp, self.humd = DHT.read_retry(DHT.DHT22, self.dht22)
    

    def print_temp(self) -> None:
        self.check_temp()
        print("Temperatura: \t{0:0.1f}\nUmidade: \t{1:0.1f}".format(self.temp, self.humd))


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
                elif self.room.state['AL_BZ']: # turns buzzer off if already on
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
        if time() - self._lights_timer > 15.0:
            self.room.set_low('L_01')
            self.room.set_low('L_02')
            self.lights_timer = None
            self.recent_pres = False

