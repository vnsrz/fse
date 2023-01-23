from comandos import Comandos
from controle import Controle
from datetime import datetime
from gpio import Temperatura
from time import sleep
from threading import Event
from threading import Thread
import signal
import sys
import os


MENU ="""
--------------------Menu--------------------
Aperte enter para atualizar as temperaturas

    [1] Alterar os valores de kp, ki, e kd
    [2] Alterar a temperatura de referência
--------------------------------------------

"""

event = Event()

def write_log(t_int, t_ext, t_ref, sinal_v, sinal_r):
            if not os.path.isfile('./log.csv'):
                with open('log.csv', 'a', encoding='UTF8') as f:
                    f.write('data,temp_interna,temp_externa,temp_referencia,acionamento_ventoinha,acionamento_resistor\n') 
            with open('log.csv', 'a', encoding='UTF8') as f:
                f.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")},{t_int:.2f},{t_ext:.2f},{t_ref:.2f},{sinal_v},{sinal_r}\n')


def cls() -> None:
        os.system('clear')


def menu(ctrl:Controle, temp:Temperatura):
    while True:
        if event.is_set():
            print('menu fechando')
            break

        print(f'temp ref:\t {ctrl.temp_referencia:.2f} °C\ntemp int:\t {ctrl.temp_interna:.2f} °C\ntemp ext:\t {ctrl.temp_externa:.2f} °C')
        print(MENU)
        escolha = input()

        if escolha == '1':
            kp = input('digite o valor de kp: ')
            ki = input('digite o valor de ki: ')
            kd = input('digite o valor de kd: ')
            temp.altera_param(kp, ki, kd)
        elif escolha == '2':
            ctrl.temp_usuario = float(input('digite a temperatura desejada: '))
            ctrl.cmd.envia_sinal_referencia(ctrl.temp_usuario)
        

def main():
    def signal_handler(sig, frame):
        print('\nSIGINT recebido')
        event.set()
        temp.join()
        ctrl.join()
        sys.exit(0)
    
    matricula = b'\x00\x08\x01\x04'

    ctrl = Controle(event, matricula)
    temp = Temperatura(event, ctrl)
    thread_main = Thread(target=menu, args=[ctrl, temp])

    ctrl.start()
    temp.start()
    thread_main.start()

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        write_log(ctrl.temp_interna, ctrl.temp_referencia, ctrl.temp_externa, temp.sinal_ventoinha, temp.sinal_resistor)
        sleep(1)


if __name__ == '__main__':
    main()