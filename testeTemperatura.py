import time
import dht
from machine import Pin

DHT_PIN = 15

sensor = dht.DHT11(Pin(DHT_PIN))

while True:
    try:
        print("Starting measure")
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print("Temperatura: {} C, Humidity: {} %".format(temp, hum))
    except OSError as e:
        print("DHT read error:", e)
    time.sleep(1)