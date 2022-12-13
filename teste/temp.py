import Adafruit_DHT

def get_temp(DHT_PIN) -> tuple:
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT_PIN)
    if humidity is not None and temperature is not None:
        return humidity, temperature

def print_temp(DHT_PIN):
    humidity, temperature = get_temp(DHT_PIN)

    if humidity is not None and temperature is not None:
        print("Temperatura \t\t{0:0.1f}ºC\nUmidade \t\t{1:0.1f}%".format(temperature, humidity))
    else:
        print("Falha ao receber os dados do sensor de umidade")

def temp_loop(DHT_PIN):
    while True:
        print_temp(DHT_PIN)