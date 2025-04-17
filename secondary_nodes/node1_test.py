import network
import espnow  # Asegúrate de que este módulo esté disponible
import time
import dht
from machine import Pin
import json

# Inicializar ESP-NOW
esp=espnow.ESPNow() 
esp.active(True)

# Configurar el sensor DHT22 en el pin 15
sensor = dht.DHT22(Pin(15))  # Cambiado a Pin 15

# Dirección MAC del nodo principal (reemplaza con la dirección real)
peer = bytes.fromhex('c4d8d595b46c')  # Cambia esto a la dirección MAC del nodo principal

# Función de callback para recibir datos
def recv_callback(msg):
    try:
        data = json.loads(msg)
        print("Mensaje recibido:", data)
        
        # Aquí puedes experimentar con diferentes lógicas de procesamiento
        # Por ejemplo, puedes agregar condiciones para manejar los datos
        if 'temperature' in data and 'humidity' in data:
            print("Datos válidos recibidos.")
        else:
            print("Datos incompletos recibidos.")
        
        # Retransmitir los datos al nodo principal
        espnow.send(peer, json.dumps(data))  # Enviar a la dirección MAC del nodo principal
    except Exception as e:
        print("Error en la recepción de datos:", e)

# Registrar la función de callback
esp.recv(recv_callback)  # Asegúrate de que esto esté correcto

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
                "mac": wlan.config('mac')  # Incluir la dirección MAC
            }
            espnow.send(peer, json.dumps(data))
            print("Datos enviados:", data)
        else:
            print("Lectura fuera de rango:", temperature, "°C", humidity, "%")
    else:
        print("Error al leer el sensor")

while True:
    send_data()  # Enviar datos al nodo principal
    time.sleep(30)  # Enviar datos cada 30 segundos
