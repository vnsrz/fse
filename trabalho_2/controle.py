from adafruit_bme280 import basic as ada
from comandos import Comandos
import threading
import board


class Controle(threading.Thread):
    est_funcionamento: bool
    temp_referencia: float
    temp_interna: float
    temp_externa: float
    temp_usuario: float
    modo_controle: bool
    est_sistema: bool
    comandos: dict

    def __init__(self, event, matricula:bytes):
        super().__init__()
        self.i2c = board.I2C()
        self.bme280 = ada.Adafruit_BME280_I2C(self.i2c, 0x76)
        self.cmd = Comandos(matricula)
        self.cmd.envia_estado_funcionamento(0)
        self.cmd.modo_controle_temp_ref(0)
        self.cmd.envia_estado_sistema(0)
        self.est_funcionamento = False
        self.modo_controle = False
        self.est_sistema = False
        self.temp_referencia = 0.0
        self.temp_interna = 0.0
        self.temp_externa = 0.0
        self.temp_usuario = 30.0
        self.event = event
        self.comandos = {
            'liga': b'\xa1\x00',
            'desliga': b'\xa2\x00',
            'inicia': b'\xa3\x00',
            'cancela': b'\xa4\x00',
            'menu': b'\xa5\x00',
        }


    def run(self):
        while True:
            if self.event.is_set():
                self.cmd.envia_estado_sistema(0)
                self.cmd.envia_estado_funcionamento(0)
                print("ctrl fechando")
                self.cmd.srl.close()
                break
            
            self.temp_interna = self.cmd.solicita_temp_interna()
            self.temp_referencia = self.cmd.solicita_temp_referencia()
            self.temp_externa = self.bme280.temperature

            comando = self.cmd.le_comandos()

            if comando == self.comandos['liga']:
                print(f'recebido:\t liga')
                self.cmd.envia_estado_sistema(1)
                self.est_sistema = True

            elif comando == self.comandos['desliga']:
                print(f'recebido:\t desliga')
                self.cmd.envia_estado_sistema(0)
                self.est_sistema = False

            elif comando == self.comandos['inicia']:
                print(f'recebido:\t inicia')
                self.cmd.envia_estado_funcionamento(1)
                self.est_funcionamento = True

            elif comando == self.comandos['cancela']:
                print(f'recebido:\t cancela')
                self.cmd.envia_estado_funcionamento(0)
                self.est_funcionamento = False

            elif comando == self.comandos['menu']:
                print(f'recebido:\t menu')
                if self.modo_controle:
                    self.cmd.modo_controle_temp_ref(False)
                else:
                    self.cmd.modo_controle_temp_ref(True)
                    self.temp_referencia = self.temp_usuario
                    self.cmd.envia_sinal_referencia(self.temp_usuario)

                self.modo_controle = not self.modo_controle
            
        