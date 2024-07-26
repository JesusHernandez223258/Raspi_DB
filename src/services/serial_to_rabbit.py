import serial
import json
import os
from src.services.rabbitmq_service import publish_message

# Configura el puerto serial y la velocidad de baudios
SERIAL_PORT = os.getenv('SERIAL_PORT', '/dev/ttyUSB0')
BAUD_RATE = int(os.getenv('BAUD_RATE', '115200'))

# Asegúrate de que el archivo `.env` contenga las variables necesarias.
# Puedes usar dotenv para cargar las variables de entorno desde un archivo .env
from dotenv import load_dotenv
load_dotenv()

# Obtén el tema MQTT desde las variables de entorno
topic = "sensor"

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Datos recibidos del sensor: {line}")  # Añadido para depuración
            try:
                data = json.loads(line)
                publish_message(topic, data)
            except json.JSONDecodeError:
                print("Error al decodificar el JSON: ", line)

if __name__ == "__main__":
    main()
