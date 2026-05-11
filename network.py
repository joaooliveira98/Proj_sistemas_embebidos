import network
import time
import urequests

ssid = 'NETLAB-0024'
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    print('Connecting to network...')
    wlan.connect(ssid, password)
    
    timeout = 15 # seconds
    start = time.time()
    
    while not wlan.isconnected():
        if time.time() - start > timeout:
            raise RuntimeError('Wi-Fi connect timeout')
        time.sleep(0.5)

url = 'http://192.168.168.100:8000/ola.txt'

r = urequests.get(url)

print(f'status: {r.status_code}')
print(f'headers: {r.headers}')
print(f'text (first 200 chars): {r.text[:200]}')

print('connected, ifconfig =', wlan.ifconfig())

r.close()