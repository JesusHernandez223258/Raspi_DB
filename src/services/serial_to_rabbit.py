import serial
import json
import os
from rabbitmq_service import publish_message

# Configura el puerto serial y la velocidad de baudios
ser = serial.Serial('/dev/ttyUSB0', 9600)

topic = os.getenv('MQTT_TOPIC')

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        try:
            data = json.loads(line)
            publish_message(topic, data)
        except json.JSONDecodeError:
            print("Error al decodificar el JSON")
