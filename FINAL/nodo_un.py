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
PRINCIPAL_MAC = b'\xc4\xd8\xd5\x95\xb4\x6c'  # MAC del principal en BYTES
SENSOR_PIN = 15
SCAN_INTERVAL = 30
MAX_RETRIES = 3

# --- INICIALIZACIÓN --- #
sensor = dht.DHT22(Pin(SENSOR_PIN))
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
e = espnow.ESPNow()
e.active(True)

# Configuración robusta de peers
try:
    e.add_peer(PRINCIPAL_MAC)
    print(f"✔ Principal vinculado: {binascii.hexlify(PRINCIPAL_MAC).decode()}")
except Exception as ex:
    print(f"❌ Error añadiendo principal: {ex}")
    machine.reset()

MY_MAC = unique_id()
vecinos = set()

# --- FUNCIONES CLAVE --- #
def escanear_vecinos():
    global vecinos
    try:
        temp_vecinos = set()
        for mac in e.get_peers():  # Versión estable
            if mac != PRINCIPAL_MAC and mac != MY_MAC:
                temp_vecinos.add(mac)
        
        vecinos = temp_vecinos
        print("🔍 Vecinos:", [binascii.hexlify(mac).decode()[:6] for mac in vecinos])
    except Exception as ex:
        print(f"⚠️ Error escaneo: {str(ex)[:50]}")

def enviar_datos(temp, hum, intentos=MAX_RETRIES):
    if intentos <= 0:
        return False

    try:
        datos = {
            "temp": float(temp),
            "hum": float(hum),
            "origen": binascii.hexlify(MY_MAC).decode()[:6]
        }
        msg = json.dumps(datos).encode('utf-8')  # Conversión segura a bytes
        
        # 1. Intento directo
        try:
            e.send(PRINCIPAL_MAC, msg)
            print(f"📤 Enviado a principal: {datos['temp']}°C")
            return True
        except Exception as ex:
            print(f"⚠️ Fallo principal ({intentos}): {str(ex)[:50]}")

        # 2. Retransmisión
        if vecinos:
            for mac in random.sample(vecinos, len(vecinos)):
                try:
                    e.send(mac, msg)
                    print(f"📡 Retrans. a {binascii.hexlify(mac).decode()[:6]}")
                    return True
                except:
                    continue

        time.sleep(1)
        return enviar_datos(temp, hum, intentos-1)
    except Exception as ex:
        print(f"❌ Error crítico: {str(ex)[:50]}")
        return False

# --- BUCLE PRINCIPAL --- #
print(f"\n⚡ Nodo {binascii.hexlify(MY_MAC).decode()[:6]} iniciado ⚡")
ultimo_escaneo = time.time()

while True:
    try:
        # Escaneo periódico
        if time.time() - ultimo_escaneo > SCAN_INTERVAL:
            escanear_vecinos()
            ultimo_escaneo = time.time()

        # Lectura y envío
        sensor.measure()
        if not enviar_datos(sensor.temperature(), sensor.humidity()):
            print("🔴 Reintentando próxima lectura")
            
        time.sleep(10)
        
    except Exception as ex:
        print(f"🔥 Error en bucle: {ex}")
        time.sleep(5)
