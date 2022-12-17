import sys
from time import sleep
from threading import Thread

def iterador(n: int) -> None:
    for _ in range(n):
        print('heey')
        sleep(1)
    
t = Thread(target=iterador, args=(15,))
t.start()

while True:
    a = input()
    print(a)