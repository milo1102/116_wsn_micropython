import network
import espnow 
import time
import dht
from machine import Pin
import json

# Inicializar ESP-NOW
e=espnow.ESPNow()
e.active(True)
peer = bytes.fromhex('c4d8d595b46c') 
e.add_peer(peer)  # Asegúrate de que esto esté correcto

# Configurar el sensor DHT22 en el pin 15
sensor = dht.DHT22(Pin(15))  # Cambiado a Pin 15


# Función de callback para recibir datos
def recv_callback(e):
    while True:  # Leer todos los mensajes esperando en el buffer
        mac, msg = e.irecv(0)  # No esperar si no hay mensajes
        if mac is None:
            return
        data = json.loads(msg)
        print("Mensaje recibido de", mac, ":", data)
        
        # Retransmitir los datos al nodo principal
        e.send(peer, json.dumps(data))  # Enviar a la dirección MAC del nodo principal


# Registrar la función de callback
e.irq(recv_callback)  # Asegúrate de que esto esté correcto

# Enviar datos al nodo principal
def send_data():
    sensor.measure()
    temperature = sensor.temperature()
    humidity = sensor.humidity()
    
    # Validar las lecturas
    if temperature is not None and humidity is not None:
        if 0 <= temperature <= 50 and 0 <= humidity <= 100:  # Rango razonable
            data = {
                "temperature": temperature,
                "humidity": humidity,
                "mac": 'c0:49:ef:9c:d7:dc'  # Incluir la dirección MAC
            }
            e.send(peer, json.dumps(data),True)
            print("Datos enviados:", data)
        else:
            print("Lectura fuera de rango:", temperature, "°C", humidity, "%")
    else:
        print("Error al leer el sensor")

while True:
    send_data()  # Enviar datos al nodo principal
    time.sleep(30)  # Enviar datos cada 30 segundos
