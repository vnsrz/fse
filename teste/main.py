import RPi.GPIO as GPIO
from time import sleep
import os

from fse.teste.temp import *
from fse.distrib.room import *

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

placa = load_json("".join([os.getcwd(), '/pinos.json']))
setup(placa)

global hum
global temp
global pessoas

LAMPADAS ="""
---------Acionar Lâmpadas---------
    [1] Lâmpada 1
    [2] Lâmpada 2
    [3] Ligar todas
    [4] Desligar todas
    [0] Retornar

"""

def estado_presenca():
    global estado_spres
    global estado_sjan
    global estado_spor
    global estado_sfum

    while(True):
        estado_spres = GPIO.input(placa['IN']['SPres'])
        if estado_spres:
            # informa central
            pass

        estado_sjan = GPIO.input(placa['IN']['SJan'])
        if estado_sjan:
            # informa central
            pass

        estado_spor = GPIO.input(placa['IN']['SPor'])
        if estado_spor:
            # informa central
            pass

        estado_sfum = GPIO.input(placa['IN']['SFum'])
        if estado_sfum:
            # informa central
            pass

    
def atualiza_estados():
    global estado_l1
    global estado_l2
    global estado_ac
    global estado_pr

    estado_l1 = GPIO.input(placa['OUT']['L_01'])
    estado_l2 = GPIO.input(placa['OUT']['L_02'])
    estado_ac = GPIO.input(placa['OUT']['AC'])
    estado_pr = GPIO.input(placa['OUT']['PR'])


atualiza_estados()

def set_high(pino) -> int:
    GPIO.output(pino, GPIO.HIGH)
    return 1


def set_low(pino) -> int:
    GPIO.output(pino, GPIO.LOW)
    return 0


def interruptor(pino) -> int:
    if GPIO.input(pino):
        return set_low(pino)
    else:
        return set_high(pino)


def desliga_sala(placa):
    for pino in placa['OUT'].values():
        set_low(pino)
    atualiza_estados()


def controla_lampadas(placa):
    global estado_l1
    global estado_l2

    acao = input(LAMPADAS)

    if(acao == '0'):
        return
    elif(acao == '1'):
        pino = placa['OUT']['L_01']
        estado_l1 = interruptor(pino)
    elif(acao == '2'):
        pino = placa['OUT']['L_02']
        estado_l2 = interruptor(pino)
    elif(acao == '3'):
        pino = placa['OUT']['L_01']
        estado_l1 = set_high(pino)
        pino = placa['OUT']['L_02']
        estado_l2 = set_high(pino)
    elif(acao == '4'):
        pino = placa['OUT']['L_01']
        estado_l1 = set_low(pino)
        pino = placa['OUT']['L_02']
        estado_l2 = set_low(pino)


def print_estados():
    if estado_l1:
        print('Lâmpada 1 \t\tligada')
    else:
        print('Lâmpada 1 \t\tdesligada')
    
    if estado_l2:
        print('Lâmpada 2 \t\tligada')
    else:
        print('Lâmpada 2 \t\tdesligada')
    
    if estado_ac:
        print('Ar-Condicionado \tligado')
    else:
        print('Ar-Condicionado \tdesligado')

    if estado_pr:
        print('Projetor \t\tligado')
    else:
        print('Projetor \t\tdesligado')


def hum_temp():
    global hum
    global temp

    while(True):
        hum, temp = get_temp(placa['DHT22'])
        sleep(2)


def main():
    global pessoas

    pessoas = 0
    GPIO.add_event_detect(placa['IN']['SC_IN'], GPIO.RISING)
    GPIO.add_event_detect(placa['IN']['SC_OUT'], GPIO.RISING)
    while True:
        if GPIO.event_detected(placa['IN']['SC_IN']):
            pessoas += 1
            print(f'Pessoas \t{pessoas}')
        if GPIO.event_detected(placa['IN']['SC_OUT']):
            pessoas -= 1
            print(f'Pessoas \t{pessoas}')


if __name__ == '__main__':
    main()
