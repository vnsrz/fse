from simple_pid import PID
import RPi.GPIO as GPIO
from time import sleep
import threading

class Temperatura(threading.Thread):
    def __init__(self, event, controle):
        super().__init__()
        self.ctrl = controle
        self.event = event

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)
        GPIO.setup(24, GPIO.OUT)    

        self.resistor = GPIO.PWM(23, 1000)
        self.ventoinha = GPIO.PWM(24, 1000)
        self.ventoinha.start(0.0)
        self.resistor.start(0.0)

        self.sinal_resistor = 0.0
        self.sinal_ventoinha = 0.0

        self.pid = PID(30.0, 0.2, 400.0, sample_time=0.5)
        self.pid.output_limits = (-100, 100)
        
    
    def clamp(self, l:float, r:float, x:float):
        return min(r, max(l, x))


    def altera_param(self, kp:float, ki:float, kd:float):
        self.pid.tunings = (kp, ki, kd)
        print(f'kp:\t {kp}\nki:\t {ki}\nkd:\t {kd}')


    def run(self):
        while True:
            if self.event.is_set():
                print("temp fechando")
                GPIO.cleanup()
                break

            if self.ctrl.est_funcionamento and self.ctrl.est_sistema:
                self.pid.setpoint = self.ctrl.temp_referencia
                pid_atual = self.pid(self.ctrl.temp_interna)

                if pid_atual > 0:
                    self.sinal_resistor = pid_atual
                    self.sinal_ventoinha = 0
                else:
                    self.sinal_resistor = 0
                    self.sinal_ventoinha = self.clamp(40, 100, -pid_atual)
                    pid_atual = -self.sinal_ventoinha

                print(f'pid:\t\t {pid_atual:.2f}')

                self.resistor.ChangeDutyCycle(self.sinal_resistor)
                self.ventoinha.ChangeDutyCycle(self.sinal_ventoinha)

                self.ctrl.cmd.envia_sinal_controle(int(pid_atual))

                sleep(5)
