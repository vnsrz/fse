from time import sleep
import json
import sys

import RPi.GPIO as gp

from temp import *
from setup import *

gp.setmode(gp.BCM)
gp.setwarnings(False)

placa = load_json(sys.argv[1])
setup(placa)

estado_l1 = gp.input(placa['OUT']['L_01'])
estado_l2 = gp.input(placa['OUT']['L_02'])
estado_ac = gp.input(placa['OUT']['AC'])
estado_pr = gp.input(placa['OUT']['PR'])

CONSOLE ="""
--------Painel de Controle-------
    [1] Acionar as lâmpadas
    [2] Acionar o ar-condicionado
    [3] Acionar o projetor
    [4] Checar a temperatura
    [5] Checar estados
    [6] Desligar tudo
    [0] Terminar o programa

"""

LAMPADAS ="""
---------Acionar Lâmpadas---------
    [1] Lâmpada 1
    [2] Lâmpada 2
    [3] Todas
    [0] Retornar

"""

def set_high(pino) -> bool:
    gp.output(pino, gp.HIGH)
    return True


def set_low(pino) -> bool:
    gp.output(pino, gp.LOW)
    return False


def interruptor(pino) -> bool:
    if gp.input(pino):
        return set_low(pino)
    else:
        return set_high(pino)


def desliga_sala(placa):
    for pino in placa['OUT'].values():
        set_low(pino)
    print('\nTodas as cargas foram desligadas')


def controla_lampadas(placa):
    acao = input(LAMPADAS)
    if(acao == '0'):
        return
    elif(acao == '1'):
        pino = placa['OUT']['L_01']
        estado_l1 = interruptor(pino)
        print('\nLâmpada 1 ligada') if estado_l1 else print('\nLâmpada 1 desligada')
    elif(acao == '2'):
        pino = placa['OUT']['L_02']
        estado_l2 = interruptor(pino)
        print('\nLâmpada 2 ligada') if estado_l2 else print('\nLâmpada 2 desligada')
    elif(acao == '3'):
        pino = placa['OUT']['L_01']
        estado_l1 = interruptor(pino)
        print('\nLâmpada 1 ligada') if estado_l1 else print('\nLâmpada 1 desligada')
        pino = placa['OUT']['L_02']
        estado_l2 = interruptor(pino)
        print('Lâmpada 2 ligada') if estado_l2 else print('Lâmpada 2 desligada')


def print_estados():
    if estado_l1:
        print('Lâmpada 1: ligada')
    else:
        print('Lâmpada 1: desligada')
    
    if estado_l2:
        print('Lâmpada 2: ligada')
    else:
        print('Lâmpada 2: desligada')
    
    if estado_ac:
        print('Ar-condicionado: ligado')
    else:
        print('Ar-condicionado: desligado')

    if estado_pr:
        print('Projetor: ligado')
    else:
        print('Projetor: desligado')


def main():
    ativo = True

    while(ativo):
        acao = input(CONSOLE)
        if(acao == '0'): # desliga
            ativo = False
        elif(acao == '1'): # lamp
            controla_lampadas(placa)
        elif(acao == '2'): # ac
            pino = placa['OUT']['AC']
            estado_ac = interruptor(pino)
            print('\nAC ligado') if estado_ac else print('\nAC desligado')
        elif(acao == '3'): # projetor
            pino = placa['OUT']['PR']
            estado_pr = interruptor(pino)
            print('\nProjetor ligado') if estado_pr else print('\nProjetor desligado')
        elif(acao == '4'): # temp
            print_temp(placa['DHT22'])
        elif(acao == '5'): # estados
            print_estados()
        elif(acao == '6'): # desliga sala
            desliga_sala(placa)


if __name__ == '__main__':
    main()
