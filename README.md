# Configuración ESP32 con MicroPython para macOS

## Pasos de Instalación para macOS

### 1. Instalar Thonny IDE
1. Descargar Thonny para macOS desde https://thonny.org/
   - Descargar el archivo .pkg para macOS
   - Doble clic en el archivo descargado para instalar
   - Arrastrar Thonny a la carpeta Aplicaciones

### 2. Instalar Driver USB-UART para ESP32
1. Descargar el driver CP210x para macOS desde:
   https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
2. Instalar el driver:
   - Abrir el archivo descargado (.dmg)
   - Doble clic en el instalador
   - Seguir las instrucciones de instalación
   - Reiniciar la computadora después de la instalación

### 3. Instalar dependencias Python
```bash
pip3 install -r requirements.txt
```

### 4. Descargar MicroPython Firmware
1. Visitar https://micropython.org/download/esp32/
2. Descargar la última versión estable del firmware (ejemplo: esp32-20230426-v1.20.0.bin)

### 5. Flashear ESP32
1. Conectar ESP32 al puerto USB
2. Abrir Terminal y ejecutar:
```bash
# Identificar el puerto (reemplazar X con el número correcto)
ls /dev/tty.usbserial-*
# Ejemplo: /dev/tty.usbserial-0001

# Borrar flash
esptool.py --port /dev/tty.usbserial-XXXX erase_flash

# Flashear MicroPython
esptool.py --chip esp32 --port /dev/tty.usbserial-XXXX --baud 460800 write_flash -z 0x1000 esp32-20230426-v1.20.0.bin
```

### 6. Configurar Thonny para ESP32
1. Abrir Thonny
2. Ir a "Thonny" -> "Preferences" -> "Interpreter"
3. Seleccionar "MicroPython (ESP32)" en el menú desplegable
4. En "Port", seleccionar el puerto que comienza con "/dev/tty.usbserial-"
5. Click en "OK"

## Verificación de la Instalación
1. Conectar ESP32 al Mac
2. Abrir Terminal y ejecutar:
```bash
ls /dev/tty.usbserial-*
```
Deberías ver un dispositivo listado.

## Prueba Básica
1. Abrir Thonny
2. Crear nuevo archivo con el siguiente código:

```python
from machine import Pin
import time

led = Pin(2, Pin.OUT)  # LED integrado en GPIO2

while True:
    led.value(not led.value())  # Toggle LED
    time.sleep(1)  # Esperar 1 segundo
```

3. Guardar como 'blink_test.py' en la ESP32
4. Ejecutar y verificar que el LED parpadea

## Solución de Problemas en macOS
1. Si el puerto no aparece:
   - Verificar que el driver CP210x está instalado
   - Desconectar y reconectar el ESP32
   - Reiniciar la computadora

2. Si hay problemas de permisos:
   ```bash
   # Dar permisos al puerto (reemplazar XXXX con el número correcto)
   sudo chmod 666 /dev/tty.usbserial-XXXX
   ```

3. Si Thonny no reconoce el puerto:
   - Cerrar Thonny
   - Desconectar y reconectar ESP32
   - Volver a abrir Thonny

## Próximos Pasos
Una vez configurado el entorno básico, procederemos con:
1. Implementación de la lectura del sensor DHT22
2. Configuración de la red mesh
3. Desarrollo de la interfaz web

## Notas Importantes
- En macOS, los puertos del ESP32 aparecen como `/dev/tty.usbserial-XXXX`
- Asegúrate de tener los permisos correctos para acceder al puerto USB
- Si tienes problemas con pip, puedes usar `pip3` en su lugar
- Thonny en macOS se encuentra en la carpeta Aplicaciones
