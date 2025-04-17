# main_chart.py
import network
import espnow
import time
import json
import socket
import binascii
import machine
import _thread

# --- CONFIGURACIÓN --- #
WIFI_SSID = "Carrillo"
WIFI_PASS = "andre2712m"
HTTP_PORT = 80
MAX_WIFI_RETRIES = 15  # Aumentamos los intentos de conexión WiFi

# MACs (¡Verifica que sean correctas!)
PRINCIPAL_MAC = b'\xc4\xd8\xd5\x95\xb4\x6c'
SUB_NODES = {
    "NODO_A": b'\xc0\x49\xef\x9c\xd7\xdc',
    "NODO_B": b'\xcc\xdb\xa7\x32\xb7\x40',
    "NODO_C": b'\xcc\xdb\xa7\x33\x97\x94'
}

# --- INICIALIZACIÓN --- #
data_store = {node: {"temp": [], "hum": []} for node in SUB_NODES}
server_socket = None

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"\nConectando a WiFi '{WIFI_SSID}'...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        
        for i in range(MAX_WIFI_RETRIES):
            if wlan.isconnected():
                break
            print(f"Intento {i+1}/{MAX_WIFI_RETRIES}... Estado: {wlan.status()}")
            time.sleep(2)  # Aumentamos el delay entre intentos
    
    if wlan.isconnected():
        print(f"\n✅ WiFi conectado!")
        print(f"IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("\n❌ Fallo de conexión WiFi")
        print(f"Estado final: {wlan.status()}")
        print("Verifica:")
        print("- Credenciales correctas")
        print("- Señal WiFi suficiente")
        print("- Router en 2.4GHz")
        return False

def init_esp_now():
    e = espnow.ESPNow()
    e.active(True)
    for mac in SUB_NODES.values():
        e.add_peer(mac)
    print("\n✅ ESP-NOW listo. Nodos vinculados:")
    for name, mac in SUB_NODES.items():
        print(f"  - {name}: {binascii.hexlify(mac).decode()}")
    return e

def start_http_server():
    global server_socket
    
    if server_socket:
        server_socket.close()
        time.sleep(1)
    
    try:
        addr = socket.getaddrinfo('0.0.0.0', HTTP_PORT)[0][-1]
        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(addr)
        server_socket.listen(1)
        print(f"\n🌐 Servidor HTTP iniciado en http://{addr[0]}")
        
        while True:
            try:
                cl, addr = server_socket.accept()
                request = cl.recv(1024).decode()
                
                if '/data' in request:
                    cl.send('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n')
                    cl.send(json.dumps(data_store).encode())
                else:
                    with open('index.html', 'r') as f:
                        cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
                        cl.send(f.read().encode())
                cl.close()
            except Exception as e:
                print(f"⚠️ Error HTTP: {e}")
    except Exception as e:
        print(f"❌ Error en servidor: {e}")
        raise

def espnow_listener(esp):
    while True:
        mac, msg = esp.recv()
        if mac:
            try:
                data = json.loads(msg.decode())
                node_name = next((n for n, m in SUB_NODES.items() if m == mac), "Desconocido")
                if "temp" in data and "hum" in data:
                    data_store[node_name]["temp"].append(data["temp"])
                    data_store[node_name]["hum"].append(data["hum"])
                    print(f"📊 {node_name}: Temp={data['temp']}°C, Hum={data['hum']}%")
            except Exception as e:
                print(f"❌ Error en datos ESP-NOW: {e}")

def main():
    print("\n=== INICIANDO NODO PRINCIPAL ===")
    
    if not connect_wifi():
        print("\nReiniciando en 10 segundos...")
        time.sleep(10)
        machine.reset()
    
    esp = init_esp_now()
    _thread.start_new_thread(espnow_listener, (esp,))
    start_http_server()  # Bloqueante

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n🔥 Error crítico: {e}")
        time.sleep(10)
        machine.reset()