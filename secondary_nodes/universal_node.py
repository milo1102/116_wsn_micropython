# Nodo_Universal.py
import network
import espnow
import time
import json
from machine import Pin, unique_id
import dht
import binascii
import random

# --- CONFIGURACIÓN --- #
PRINCIPAL_MAC = b'\xc4\xd8\xd5\x95\xb4\x6c'  # MAC del principal (¡CAMBIAR!)
SENSOR_PIN = 15                              # Pin del DHT22
SCAN_INTERVAL = 30                           # Segundos entre escaneos

# --- INICIALIZACIÓN --- #
sensor = dht.DHT22(Pin(SENSOR_PIN))
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
e = espnow.ESPNow()
e.active(True)
e.add_peer(PRINCIPAL_MAC)  # Siempre conectado al principal
MY_MAC = unique_id()
vecinos = {}                # Diccionario de nodos vecinos: {MAC: timestamp}
ultimo_vecino = None        # Para rotación de retransmisiones

# --- FUNCIONES --- #
def escanear_vecinos():
    """Descubre nodos cercanos (excepto principal y sí mismo)."""
    global vecinos
    temp_vecinos = {}
    for mac in e.peers:
        if mac != PRINCIPAL_MAC and mac != MY_MAC:
            temp_vecinos[mac] = time.time()
    vecinos = temp_vecinos
    print("🔍 Vecinos:", [binascii.hexlify(mac).decode() for mac in vecinos.keys()])

def enviar_datos(temp, hum, max_saltos=3):
    """Envía datos al principal o retransmite a vecinos (con rotación)."""
    global ultimo_vecino

    # Validar datos del sensor
    try:
        temp = float(temp)
        hum = float(hum)
    except:
        print("❌ Datos del sensor inválidos")
        return

    # Construir mensaje
    datos = {
        "temp": round(temp, 1),
        "hum": round(hum, 1),
        "origen": binascii.hexlify(MY_MAC).decode(),
        "saltos_restantes": max_saltos
    }

    # 1. Intentar enviar al principal primero
    try:
        e.send(PRINCIPAL_MAC, json.dumps(datos), True)
        print(f"📤 Enviado al principal: Temp={datos['temp']}°C, Hum={datos['hum']}%")
        return
    except:
        pass  # Si falla, continuar con retransmisión

    # 2. Retransmitir a un vecino (excluyendo el último usado)
    if vecinos:
        vecinos_disponibles = [mac for mac in vecinos if mac != ultimo_vecino] or list(vecinos.keys())
        vecino_mac = random.choice(vecinos_disponibles)
        try:
            e.send(vecino_mac, json.dumps(datos), True)
            ultimo_vecino = vecino_mac  # Actualizar último usado
            print(f"📡 Retransmitiendo a {binascii.hexlify(vecino_mac).decode()}")
        except Exception as ex:
            print(f"⚠️ Error retransmitiendo: {ex}")
            if max_saltos > 1:
                enviar_datos(temp, hum, max_saltos - 1)  # Reintentar
    else:
        print("⚠️ No hay nodos vecinos para retransmitir")

# --- BUCLE PRINCIPAL --- #
print(f"🚀 Nodo iniciado (MAC: {binascii.hexlify(MY_MAC).decode()})")
ultimo_escaneo = time.time()

while True:
    # Escanear vecinos periódicamente
    if time.time() - ultimo_escaneo > SCAN_INTERVAL:
        escanear_vecinos()
        ultimo_escaneo = time.time()

    # Leer sensor y enviar datos
    try:
        sensor.measure()
        enviar_datos(sensor.temperature(), sensor.humidity())
    except Exception as ex:
        print(f"❌ Error en sensor: {ex}")

    time.sleep(10)  # Intervalo entre lecturas