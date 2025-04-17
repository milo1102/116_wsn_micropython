import network
import espnow
import time
import json
import gc
import socket

# Configuración
SSID = 'Carrillo'
PASSWORD = 'andre2712m'
SUB_NODE_A_MAC = b'\xc0\x49\xef\x9c\xd7\xdc'
SUB_NODE_B_MAC = b'\xcc\xdb\xa7\x32\xb7\x40'
SUB_NODE_C_MAC = b'\xcc\xdb\xa7\x33\x97\x94'

# Almacenamiento con datos de ejemplo (para prueba inicial)
data_store = {
    "Zona 1": [25.5, 26.0, 25.7],  # Datos de ejemplo
    "Zona 2": [30.1, 29.8, 30.2],
    "Zona 3": [22.3, 22.5, 22.4]
}

def init_esp_now():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Conectado a WiFi. IP:", wlan.ifconfig()[0])
    
    e = espnow.ESPNow()
    e.active(True)
    e.add_peer(SUB_NODE_A_MAC)
    e.add_peer(SUB_NODE_B_MAC)
    e.add_peer(SUB_NODE_C_MAC)
    return e

def recv_callback(e):
    while True:
        mac, msg = e.irecv(0)
        if mac is None:
            break
        try:
            data = json.loads(msg.decode())
            zone = data["zone"]
            value = data["value"]
            data_store[zone].append(value)
            print(f"Dato recibido: {zone} = {value}")
        except Exception as e:
            print("Error en datos:", e)

def start_http_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Servidor listo en http://{}".format(addr[0]))

    while True:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()
        
        response = ""
        if '/data' in request:
            cl.send('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n')
            cl.send(json.dumps(data_store).encode())
        else:
            cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
            with open("index.html", "r") as f:
                html = f.read()
            cl.send(html.encode())
        cl.close()

def main():
    esp = init_esp_now()
    esp.irq(recv_callback)
    start_http_server()

try:
    main()
except KeyboardInterrupt:
    print("Servidor detenido")