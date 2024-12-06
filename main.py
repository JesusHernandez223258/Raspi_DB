import serial
import json
import os
import paho.mqtt.client as mqtt
import random
import time
import threading
import sqlite3

# Configuración de MQTT
mqttUrl = "52.4.219.175"
options = {
    'username': "guest",
    'password': "guest"
}
topic = os.getenv('MQTT_TOPIC', 'sensor')

# Configuración del puerto serial
serial_enabled = True  # Cambiar a True para usar datos reales
serial_port = '/dev/ttyUSB0'
baud_rate = 115200

# Cliente MQTT global
mqtt_client = None

# Conectar al servidor MQTT
def connect_to_mqtt():
    global mqtt_client
    try:
        mqtt_client = mqtt.Client()
        mqtt_client.username_pw_set(options['username'], options['password'])
        mqtt_client.connect(mqttUrl)

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Conectado al broker MQTT. Suscrito al tema: {topic}")
                client.subscribe(topic, qos=1)
            else:
                print(f"Error de conexión con código {rc}")

        mqtt_client.on_connect = on_connect
        mqtt_client.loop_start()
        return mqtt_client
    except Exception as e:
        print(f"Error al conectar al broker MQTT: {e}")
        return None

# Publicar mensajes en MQTT
def publish_message(topic, message):
    try:
        if mqtt_client:
            mqtt_client.publish(topic, json.dumps(message), qos=1)
            print(f"Mensaje publicado: {json.dumps(message)}")
        else:
            print("Cliente MQTT no disponible para publicar mensajes.")
    except Exception as e:
        print(f"Error al publicar el mensaje: {e}")

# Generar datos simulados
def generate_simulated_data():
    return {
        "id_user": "20aea1e5-0117-4411-a6d0-0c30b2cd6a50",
        "voltaje": round(random.uniform(110, 220), 2),
        "ampers": round(random.uniform(0.1, 10), 2),
        "whs": round(random.uniform(0.1, 10), 2),
        "consumo_kwh": round(random.uniform(0.1, 1), 4)
    }

# Guardar datos en SQLite
def save_data_to_db(data):
    try:
        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                            id_user TEXT, voltaje REAL, ampers REAL, 
                            whs REAL, consumo_kwh REAL)''')
        cursor.execute('''INSERT INTO sensor_data (id_user, voltaje, ampers, whs, consumo_kwh)
                          VALUES (?, ?, ?, ?, ?)''', 
                          (data['id_user'], data['voltaje'], data['ampers'], data['whs'], data['consumo_kwh']))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al guardar datos en la base de datos: {e}")

# Procesar datos seriales o simulados
def process_data():
    while True:
        try:
            if serial_enabled:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    print(f"Datos recibidos: {line}")
                    parts = line.split(", ")
                    data = {
                        "id_user": parts[0].split(":")[1],
                        "voltaje": float(parts[1].split(":")[1].replace("V", "")),
                        "ampers": float(parts[2].split(":")[1].replace("A", "")),
                        "whs": float(parts[3].split(":")[1].replace("W", "")),
                        "consumo_kwh": float(parts[4].split(":")[1].replace("kWh", ""))
                    }
            else:
                data = generate_simulated_data()

            save_data_to_db(data)
            publish_message(topic, data)
        except Exception as e:
            print(f"Error procesando datos: {e}")
        time.sleep(5)

# Reconectar automáticamente
def reconnect_mqtt():
    global mqtt_client
    while True:
        if not mqtt_client:
            print("Intentando reconectar a MQTT...")
            mqtt_client = connect_to_mqtt()
            if mqtt_client:
                print("Reconexión exitosa.")
                break
        time.sleep(5)

# Inicializar y ejecutar
if serial_enabled:
    try:
        ser = serial.Serial(serial_port, baud_rate)
    except Exception as e:
        print(f"Error al inicializar el puerto serial: {e}")

mqtt_client = connect_to_mqtt()
if not mqtt_client:
    threading.Thread(target=reconnect_mqtt).start()

data_thread = threading.Thread(target=process_data)
data_thread.start()
