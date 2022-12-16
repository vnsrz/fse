from threads import *
import socket
import sys

CONSOLE ="""
--------Painel de Controle-------
    [1] Acionar as lâmpadas
    [2] Acionar o ar-condicionado
    [3] Acionar o projetor
    [4] Desligar tudo
    [0] Terminar o programa

"""

def limpa_tela(n):
    for _ in range(n):
        print()


def main():
    host = '192.168.1.103' # sala 1 rasp42
    port = 34315
    # host = sys.argv[1]
    # port = int(sys.argv[2])

    sc = ServerConnectionThread(host, port)
    sc.start()

    while True:
        if sc.sockets:
            st = ServerThread(sc)
        st.start()


def console():
    salas = ['sala 1', 'sala 2']

    while True:
        i = 1
        limpa_tela(30)
        print("Escolha a sala:")
        for sala in salas:
            print(f'[{i}] {sala}')
            i += 1
        print()
        action = input()
        


# def main():
#     global estado_ac
#     global estado_pr
#     ativo = True

#     while(ativo):
#         limpa_tela(30)
#         dist.print_temp(dist.placa['DHT22'])
#         dist.print_estados()
#         acao = input(CONSOLE)
        
#         if(acao == '0'): # desliga
#             ativo = False

#         elif(acao == '1'): # lamp
#             limpa_tela(30)
#             print('Lâmpada 1 \t\tligada') if dist.estado_l1 else print('Lâmpada 1 \t\tdesligada')
#             print('Lâmpada 2 \t\tligada') if dist.estado_l2 else print('Lâmpada 2 \t\tdesligada') 
#             dist.controla_lampadas(dist.placa)

#         elif(acao == '2'): # ac
#             pino = dist.placa['OUT']['AC']
#             estado_ac = dist.interruptor(pino)

#         elif(acao == '3'): # projetor
#             pino = dist.placa['OUT']['PR']
#             estado_pr = dist.interruptor(pino)

#         elif(acao == '4'): # desliga sala
#             dist.desliga_sala(dist.placa)


if __name__ == '__main__':
    main()
