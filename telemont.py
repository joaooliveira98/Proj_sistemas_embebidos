from os import wait
import random
import math
from time import time
import requests
import machine

# --- Configurações Globais ---
debug_mode = True
equipment_id = 10
endpoint = "http://servidor:8000/temperatura"
token_JWT = ''
pins = dict()

def conectar_wifi():
    pass

def sincronizar_relogio_ntp():
    pass

def configurar_pinos_GPIO_sensores():
    pass

def setup():
    pins['Pin2'] = machine.Pin('Pin2', machine.Pin.OUT)
    conectar_wifi()
    sincronizar_relogio_ntp()
    if(not debug_mode):
        configurar_pinos_GPIO_sensores()

def obter_timestamp_formatado(): # Formato: YYYY-MM-DD HH:MM:SS
    time()
    pass

def random_number_between(max:float, min:float, decimal_places) -> float:
    return (math.floor((random.random() * (max - min + 1))*10**decimal_places)/10**decimal_places) + min

def ler_sensor_fisico(pin):
    pass

def piscar_LED_feedback():
    pass

def loop():
    t0 = 0.0, t1 = 0.0, t2 = 0.0
    agora = obter_timestamp_formatado() # Formato: YYYY-MM-DD HH:MM:SS
    # D) Lógica de Aquisição
    if debug_mode == True:
        # Geração de valores simulados
        t0 = random_number_between(15.0, 30.0, 2)
        t1 = random_number_between(20.0, 45.0, 2)
        t2 = random_number_between(10.0, 25.0, 2)
    else:
        # Leitura de sensores reais
        t0 = ler_sensor_fisico('Pin0')
        t1 = ler_sensor_fisico('Pin1')
        t2 = ler_sensor_fisico('Pin3')
    # E) Construção do Objeto JSON
    payload = {
    "Equipamento_ID": equipment_id,
    "DataHora": agora,
    "Temp0": t0,
    "Temp1": t1,
    "Temp2": t2
    }
    # Envio Seguro via API
    headers = {"Authorization": "Bearer " + token_JWT, "Content-Type": "application/json"}
    resposta = requests.post(endpoint, data=payload, headers=headers)
    if resposta.status == 201:
        piscar_LED_feedback()
        wait(1000) # Intervalo de atualização