import adafruit_dht as DHT
import RPi.GPIO as GPIO
import json
import board

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
        self.state = {key: False for key in self.out}
        self.dht22_pin = file['sensor_temperatura'][0]['gpio']
        
        if self.dht22_pin == 18:
            self.dht22 = DHT.DHT22(board.D18) #self.dht22_pin
        elif self.dht22_pin == 4:
            self.dht22 = DHT.DHT22(board.D4) #self.dht22_pin

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

        self.all_off()
    

    def all_off(self) -> None:
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


    def check_temp(self) -> int:
        try:
            self.temp = self.dht22.temperature
            self.humd = self.dht22.humidity
            return 0
        except RuntimeError:
            return 1
            #sleep(2)
            #self.check_temp()
        #self.temp, self.humd = DHT.read_retry(DHT.DHT22, self.dht22)
    

    def print_temp(self) -> None:
        if self.check_temp():
            print("Falha ao recuperar temperatura e humidade.")
        else:
            print("Temperatura: \t{0:0.1f}\nUmidade: \t{1:0.1f}".format(self.temp, self.humd))


    def print_ppl(self) -> None:
        print(f"Pessoas: \t{self.ppl_qty}\n")
