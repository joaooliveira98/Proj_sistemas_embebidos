import random
import math
import time
import urequests
import machine
from machine import Pin
from machine import Timer
from machine import RTC
import dht
import json
import network
import ntptime

# --- Configurações Globais ---
debug_mode = True
equipment_id = 10
endpoint = "http://192.168.168.100:8000/temperatura"
ntpserver = "192.168.168.100"
token_endpoint = "http://192.168.168.100:8000/get-token"
#ntpserver = "time1.google.com"
ssid = 'NETLAB-0024'
#ssid = 'freeipluso'
password = ''
token_JWT = {"value":''}
pins = dict()

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)

        timeout = 15 # seconds
        start = time.time()

        while not wlan.isconnected():
            if time.time():
                raise RuntimeError('Wi-Fi connect timeout')
            time.sleep(0.5)

    print('connected, ifconfig =', wlan.ifconfig())

def sincronizar_relogio_ntp():
    rtc = RTC()
    rtc.datetime((2026, 5, 21, 2, 10, 32, 36, 0))
    try:
        ntptime.host = ntpserver
        ntptime.settime() 
        print("Time synced to UTC:", time.localtime())
    except Exception as e:
        print(f"Failed to sync with NTP server {ntpserver}:", e)

def buscar_token():
    try:
        resposta = urequests.request('POST',token_endpoint, json={})
        print("Using: ",token_endpoint,", token request → ",resposta.status_code,resposta.text)
        token_JWT["value"] = resposta.json().get("access_token")
        print("gotten",token_JWT)
    except Exception as e:
        print("Token request failed: ",e)

def configurar_pinos_GPIO_sensores():
    pins['Pin15'] = dht.DHT11(Pin(15))

def setup():
    pins['Pin2'] = machine.Pin(2, machine.Pin.OUT)
    conectar_wifi()
    sincronizar_relogio_ntp()
    buscar_token()
    if(not debug_mode):
        configurar_pinos_GPIO_sensores()

def obter_timestamp_formatado(): # Formato: YYYY-MM-DD HH:MM:SS
    t = time.time()
    time_structured = time.gmtime(t)
    timeStr = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        time_structured[0],  # year
        time_structured[1],  # month
        time_structured[2],  # day
        time_structured[3],  # hour
        time_structured[4],  # minute
        time_structured[5],  # second
    )
    return timeStr

def random_number_between(max:float, min:float, decimal_places) -> float:
    return round((math.floor((random.random() * (max - min + 1))*10**decimal_places)/10**decimal_places) + min,decimal_places)

def ler_sensor_fisico(pin):
    if pin in pins:
        pins[pin].measure()
        temp = pins[pin].temperature()
        print(temp)
        return temp
    else:
        return None

def piscar_LED_feedback():
    pins['Pin2'].on()
    tim = Timer(0)
    tim.init(period=1000, mode=Timer.ONE_SHOT, callback=lambda t: pins['Pin2'].off())

def loop():
    t0 = 0.0
    t1 = 0.0
    t2 = 0.0
    agora = obter_timestamp_formatado() # Formato: YYYY-MM-DD HH:MM:SS
    # D) Lógica de Aquisição
    if debug_mode == True:
        # Geração de valores simulados
        t0 = random_number_between(15.0, 30.0, 2)
        t1 = random_number_between(20.0, 45.0, 2)
        t2 = random_number_between(10.0, 25.0, 2)
    else:
        # Leitura de sensores reais
        t0 = ler_sensor_fisico('Pin15') or 0
        t1 = ler_sensor_fisico('Pin20') or 0
        t2 = ler_sensor_fisico('Pin25') or 0
    # E) Construção do Objeto JSON
    payload = f"{equipment_id},{agora},{t0},{t1},{t2}"
    #payload = json.dumps(payload)
    # Envio Seguro via API
    #headers = {"Content-Type": "application/json"}
    print("loop: ",token_JWT["value"])
    headers = {"Authorization": "Bearer " + token_JWT["value"], "Content-Type": "application/json"}
    print(headers)
    print(payload)
    resposta = urequests.request('POST',endpoint, data=payload, headers=headers)
    print(resposta.status_code,resposta.text)
    if resposta.status_code == 201 or resposta.status_code == 200:
        piscar_LED_feedback()
        print("Success")
        time.sleep(1) # Intervalo de atualização
    else:
        buscar_token()
        resposta = urequests.request('POST',endpoint, data=payload, headers=headers)
        print(resposta.status_code,resposta.text)
        if resposta.status_code == 201 or resposta.status_code == 200:
            piscar_LED_feedback()
            print("Success")
            time.sleep(1) # Intervalo de atualização

setup()

loop()