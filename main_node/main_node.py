import network
import espnow
import time
import json

# Inicializar el Wi-Fi en modo punto de acceso (AP)
def setup_wifi():
    # Crear un punto de acceso
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='MiRedESPNow', password='mi_contraseña', authmode=network.AUTH_WPA2_PSK)

    # Esperar a que el AP esté activo
    while not ap.active():
        print("Esperando a que el punto de acceso esté activo...")
        time.sleep(1)

    print("Punto de acceso configurado:", ap.ifconfig())



# Inicializar el Wi-Fi en modo estación
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Conectar a la red Wi-Fi
    SSID = 'Carrillo'  # Reemplaza con tu SSID
    PASSWORD = 'andre2712m'  # Reemplaza con tu contraseña
    wlan.connect(SSID, PASSWORD)

    # Esperar a que se conecte
    while not wlan.isconnected():
        print("Conectando a la red Wi-Fi...")
        time.sleep(1)

    print("Conectado a la red Wi-Fi:", wlan.ifconfig())

# Configurar ESP-NOW
def setup_esp_now():

    global esp 
    
    # Inicializar ESP-NOW
    esp = espnow.ESPNow()
    esp.active(True)  # Activar ESP-NOW
    print("ESP-NOW inicializado y activo. Esperando conexiones de nodos.")
 # Registrar la función de callback para recibir datos

# Inicializar un diccionario para almacenar los datos recibidos
received_data = {}

# Definir la función de callback para recibir datos
def recv_callback(e):
    while True:  # Leer todos los mensajes esperando en el buffer
        mac, msg = e.irecv(0)  # No esperar si no hay mensajes
        if mac is None:
            return
        
        data = json.loads(msg)
        mac_address = data.get("mac")
        
        # Verificar si ya se ha recibido datos de este nodo en el último tiempo
        if mac_address in received_data:
            last_received_time = received_data[mac_address]['time']
            if time.time() - last_received_time < 60:  # 60 segundos de intervalo
                print("Datos duplicados ignorados de:", mac_address)
                continue  # Ignorar datos duplicados
        
        # Almacenar los datos y el tiempo de recepción
        received_data[mac_address] = {
            'data': data,
            'time': time.time()
        }
        
        print("Mensaje recibido de", mac, ":", data)

# Llamar a las funciones de configuración
setup_wifi()  # Configurar el punto de acceso para otros nodos
setup_esp_now()  # Inicializar ESP-NOW
connect_to_wifi()  # Conectar a la red Wi-Fi

# Registrar la función de callback para recibir datos
 
esp.irq(recv_callback) 
while True:
    time.sleep(2)  # Mantener el bucle activo