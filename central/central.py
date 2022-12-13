from distrib import *

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
    global estado_ac
    global estado_pr
    ativo = True

    while(ativo):
        limpa_tela(30)
        dist.print_temp(dist.placa['DHT22'])
        dist.print_estados()
        acao = input(CONSOLE)
        
        if(acao == '0'): # desliga
            ativo = False

        elif(acao == '1'): # lamp
            limpa_tela(30)
            print('Lâmpada 1 \t\tligada') if dist.estado_l1 else print('Lâmpada 1 \t\tdesligada')
            print('Lâmpada 2 \t\tligada') if dist.estado_l2 else print('Lâmpada 2 \t\tdesligada') 
            dist.controla_lampadas(dist.placa)

        elif(acao == '2'): # ac
            pino = dist.placa['OUT']['AC']
            estado_ac = dist.interruptor(pino)

        elif(acao == '3'): # projetor
            pino = dist.placa['OUT']['PR']
            estado_pr = dist.interruptor(pino)

        elif(acao == '4'): # desliga sala
            dist.desliga_sala(dist.placa)


if __name__ == '__main__':
    main()
