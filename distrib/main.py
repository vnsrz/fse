from time import sleep
import random
import json
import sys

import RPi.GPIO as gp

from temp import temp_loop

gp.setmode(gp.BCM)
gp.setwarnings(False)

text ="""
[1] Ligar as lâmpadas
[2] Checar a temperatura
[3] Nada ainda
"""

def setup(pinos):
    for pino in pinos['IN'].values():
        gp.setup(pino, gp.IN)
    for pino in pinos['OUT'].values():
        gp.setup(pino, gp.OUT)


def load_json(filename) -> dict:
    with open(filename, 'r') as f:
        file = json.load(f)
    return file


def set_high(pino) -> bool:
    gp.output(pino, gp.HIGH)
    print('ta ligada')
    return True


def set_low(pino) -> bool:
    gp.output(pino, gp.LOW)
    print('ta desligada')
    return False


def interruptor(pino):
    if gp.input(pino):
        return set_low(pino)
    else:
        return set_high(pino)
    
   

def main():
    json_file = sys.argv[1]
    placa = load_json(json_file)
    setup(placa)

    acao = input(text)

    if(acao == '1'):
        pino = placa['OUT']['AL_BZ']



    for i in range(random.randint(3,12)):
        estado = interruptor(pino)
        sleep(3)

    print(estado)

if __name__ == '__main__':
    main()
