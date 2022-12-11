import RPi.GPIO as gp
import os

from temp import *
from setup import *

gp.setmode(gp.BCM)
gp.setwarnings(False)

placa = load_json("".join([os.getcwd(), '/pinos.json']))
setup(placa)

CONSOLE ="""
--------Painel de Controle-------
    [1] Acionar as lâmpadas
    [2] Acionar o ar-condicionado
    [3] Acionar o projetor
    [4] Desligar tudo
    [0] Terminar o programa

"""

LAMPADAS ="""
---------Acionar Lâmpadas---------
    [1] Lâmpada 1
    [2] Lâmpada 2
    [3] Ligar todas
    [4] Desligar todas
    [0] Retornar

"""

def atualiza_estados():
    global estado_l1
    global estado_l2
    global estado_ac
    global estado_pr

    estado_l1 = gp.input(placa['OUT']['L_01'])
    estado_l2 = gp.input(placa['OUT']['L_02'])
    estado_ac = gp.input(placa['OUT']['AC'])
    estado_pr = gp.input(placa['OUT']['PR'])


atualiza_estados()

def set_high(pino) -> int:
    gp.output(pino, gp.HIGH)
    return 1


def set_low(pino) -> int:
    gp.output(pino, gp.LOW)
    return 0


def interruptor(pino) -> int:
    if gp.input(pino):
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
    #print("\n-------------Estados-------------")
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


def limpa_tela(n):
    for i in range(n):
        print()


def main():
    global estado_ac
    global estado_pr
    ativo = True

    while(ativo):
        limpa_tela(30)
        print_temp(placa['DHT22'])
        print_estados()
        acao = input(CONSOLE)
        if(acao == '0'): # desliga
            ativo = False
        elif(acao == '1'): # lamp
            limpa_tela(30)
            if estado_l1:
                print('Lâmpada 1 \t\tligada')
            else:
                print('Lâmpada 1 \t\tdesligada')
            if estado_l2:
                print('Lâmpada 2 \t\tligada')
            else:
                print('Lâmpada 2 \t\tdesligada')
            controla_lampadas(placa)
        elif(acao == '2'): # ac
            pino = placa['OUT']['AC']
            estado_ac = interruptor(pino)
        elif(acao == '3'): # projetor
            pino = placa['OUT']['PR']
            estado_pr = interruptor(pino)
        elif(acao == '4'): # desliga sala
            desliga_sala(placa)


if __name__ == '__main__':
    main()
