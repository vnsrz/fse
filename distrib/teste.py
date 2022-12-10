from time import sleep
import RPi.GPIO as gp

pin = 27
gp.setmode(gp.BCM)
gp.setwarnings(False)
gp.setup(pin, gp.OUT)

while True:
    gp.output(pin, gp.HIGH)
    sleep(1)
    gp.output(pin, gp.LOW)