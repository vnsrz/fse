from crc import calcula_CRC
import serial
import struct
import board

class Comandos:
    def __init__(self, matr:bytes) -> None:
        self.matricula = matr
        self.srl = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)


    def send_data(self, cmd) -> None:
        crc = calcula_CRC(cmd)
        data_crc = cmd + struct.pack('<H', crc)
        #print('data sent:\t', data_crc)
        self.srl.write(data_crc)


    def check_crc(self, data) -> bool:
        crc = calcula_CRC(data[:-2]).to_bytes(2, 'little')
        test = crc == data[-2:]
        if not test:
            print(f'crc = {crc}, rec = {data[-2:]}')
            return True
        else:
            return False


    def solicita_temp_interna(self) -> float:
        cmd = struct.pack('<BBB', 0x01, 0x23, 0xc1) + self.matricula

        self.srl.readline()
        self.send_data(cmd)
        data = self.srl.readline()
    
        while self.check_crc(data):
            self.send_data(cmd)
            data = self.srl.readline()
        
        try:
            result = struct.unpack('<BBBfH', data)
            result = result[3]
        except struct.error:
            print('struct error')
            result = self.solicita_temp_interna()

        return result
        
    def solicita_temp_referencia(self) -> float: # lembrar de pedir de novo se crc errado
        cmd = struct.pack('<BBB', 0x01, 0x23, 0xc2) + self.matricula

        self.srl.readline()
        self.send_data(cmd)
        data = self.srl.readline()
    
        while self.check_crc(data):
            self.send_data(cmd)
            data = self.srl.readline()
        
        try:
            result = struct.unpack('<BBBfH', data)
            result = result[3]
        except struct.error:
            print('struct error')
            result = self.solicita_temp_referencia()
        
        return result

        
    def envia_sinal_controle(self, cmd): 
        cmd = struct.pack('<BBB', 0x01, 0x16, 0xd1) + self.matricula + struct.pack('i', cmd)
        #print('sinal de controle enviado')
        self.send_data(cmd)


    def le_comandos(self): # Funciona as vezes
        cmd = struct.pack('<BBB', 0x01, 0x23, 0xc3) + self.matricula

        self.srl.readline()
        self.send_data(cmd)
        data = self.srl.readline()

        if not self.check_crc(data):
            result = struct.unpack('<BBBiH', data)
            received = result[3].to_bytes(2, 'little')
            return received
            
    
    def envia_sinal_referencia(self, temp:float) -> None:
        cmd = struct.pack('<BBB', 0x01, 0x16, 0xd2) + self.matricula + struct.pack('f', temp)
        print(f'temp env:\t {temp}')
        self.send_data(cmd)
    

    def envia_estado_sistema(self, state:int) -> None:
        cmd = struct.pack('<BBB', 0x01, 0x16, 0xd3) + self.matricula + struct.pack('B', state)
        self.send_data(cmd)
        data = self.srl.readline()

        if self.check_crc(data):
            result = struct.unpack('<BBBiH', data)
            received = result[3].to_bytes(2, 'little')
            #print(f'estado sis:\t {received}')
    

    def modo_controle_temp_ref(self, state) -> None:
        cmd = struct.pack('<BBB', 0x01, 0x16, 0xd4) + self.matricula + struct.pack('B', state)
        self.send_data(cmd)
        data = self.srl.readline()

        if self.check_crc(data):
            result = struct.unpack('<BBBiH', data)
            received = result[3].to_bytes(2, 'little')
            #print(f'modo ctrl:\t {received}')
    

    def envia_estado_funcionamento(self, state:int) -> None:
        cmd = struct.pack('<BBB', 0x01, 0x16, 0xd5) + self.matricula + struct.pack('B', state)
        self.send_data(cmd)
        data = self.srl.readline()

        if self.check_crc(data):
            result = struct.unpack('<BBBiH', data)
            received = result[3].to_bytes(2, 'little')
            #print(f'estado func:\t {received}')
    

    def envia_temp_ambiente(self, temp:float) -> None:
        cmd = struct.pack('<BBB', 0x01, 0x16, 0xd6) + self.matricula + struct.pack('f', temp)
        #print(f'temp env:\t {temp}')
        self.send_data(cmd)
        data = self.srl.readline()

        if self.check_crc(data):
            result = struct.unpack('<BBBfH', data)
            received = result[3].to_bytes(2, 'little')
            #print(f'tmp rec:\t {received}')


