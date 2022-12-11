import RPi.GPIO as gp
import json

def setup(pinos):
    for pino in pinos['IN'].values():
        gp.setup(pino, gp.IN)
    for pino in pinos['OUT'].values():
        gp.setup(pino, gp.OUT)


def load_json(filename) -> dict:
    with open(filename, 'r') as f:
        file = json.load(f)
    return file

