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

# Función para conectar al servidor MQTT
def connect_to_mqtt(topic):
    try:
        client = mqtt.Client()
        client.username_pw_set(options['username'], options['password'])
        client.connect(mqttUrl)

        # Función de callback cuando se conecta al servidor MQTT
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Conectado al broker MQTT. Suscrito al tema: {topic}")
                client.subscribe(topic, qos=1)
            else:
                print(f"Error de conexión con código {rc}")

        client.on_connect = on_connect
        client.loop_start()  # Iniciar el bucle para recibir mensajes
        return client
    except Exception as e:
        print(f"Error al conectar al broker MQTT: {e}")
        return None

# Función para publicar mensajes en MQTT
def publish_message(topic, message):
    try:
        client = mqtt.Client()
        client.username_pw_set(options['username'], options['password'])
        client.connect(mqttUrl)
        client.publish(topic, json.dumps(message), qos=1)
        client.disconnect()
        print(f"Mensaje publicado: {json.dumps(message)}")
    except Exception as e:
        print(f"Error al publicar el mensaje: {e}")

# Función para generar datos simulados
def generate_simulated_data():
    return {
        "id_user": "41ea7c6a-8009-450f-bae3-1aba13e9a09c",
        "voltaje": round(random.uniform(0.01, 7.34), 2),
        "ampers": round(random.uniform(0.01, 1.05), 2),
        "whs": round(random.uniform(0, 0.009), 2),
        "consumo_kwh": round(random.uniform(0.0001, 0.01), 4)
    }

# Función para guardar datos en la base de datos SQLite
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

# Función para obtener los datos no enviados desde la base de datos SQLite
def get_unsent_data_from_db():
    try:
        conn = sqlite3.connect("sensor_data.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT id_user, voltaje, ampers, whs, consumo_kwh FROM sensor_data''')
        unsent_data = cursor.fetchall()
        conn.close()
        return unsent_data
    except Exception as e:
        print(f"Error al recuperar datos de la base de datos: {e}")
        return []

# Función para enviar los datos no enviados a RabbitMQ
def send_unsent_data_to_rabbitmq(unsent_data, client, topic):
    for data in unsent_data:
        message = {
            "id_user": data[0],
            "voltaje": data[1],
            "ampers": data[2],
            "whs": data[3],
            "consumo_kwh": data[4]
        }
        try:
            client.publish(topic, json.dumps(message), qos=1)
            print(f"Datos enviados a RabbitMQ: {json.dumps(message)}")
        except Exception as e:
            print(f"Error al enviar datos a RabbitMQ: {e}")

# Función para reconectar a la cola de RabbitMQ
def reconnect_rabbitmq():
    while True:
        try:
            print("Intentando reconectar a RabbitMQ...")
            # Aquí puedes incluir la lógica de reconexión
            mqtt_client = connect_to_mqtt(topic)  # Reconectar MQTT
            if mqtt_client:
                # Recuperar y enviar los datos almacenados durante la desconexión
                unsent_data = get_unsent_data_from_db()
                send_unsent_data_to_rabbitmq(unsent_data, mqtt_client, topic)
                break  # Salir del bucle si la reconexión fue exitosa
        except Exception as e:
            print(f"Error al reconectar a RabbitMQ: {e}")
            time.sleep(5)  # Intentar de nuevo después de 5 segundos

# Configuración del puerto serial y lectura de datos
serial_enabled = False  # Cambiar a False si quieres usar datos simulados
serial_port = '/dev/ttyUSB0'

if serial_enabled:
    try:
        ser = serial.Serial(serial_port, 115200)
        print(f"Conectado al puerto serial: {ser.port}")
    except Exception as e:
        print(f"Error al conectar al puerto serial: {e}")
        exit()

# Tópico MQTT
topic = os.getenv('MQTT_TOPIC', 'sensor')

# Conectar a MQTT
mqtt_client = connect_to_mqtt(topic)
if not mqtt_client:
    print("No se pudo conectar al broker MQTT")
    exit()

# Función para leer del puerto serial y publicar los datos
def read_from_serial():
    while True:
        if serial_enabled:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(f"Datos recibidos: {line}")
                try:
                    parts = line.split(", ")
                    data = {
                        "id_user": parts[0].split(":")[1],
                        "voltaje": float(parts[1].split(":")[1].replace("V", "")),
                        "ampers": float(parts[2].split(":")[1].replace("A", "")),
                        "whs": float(parts[3].split(":")[1].replace("W", "")),
                        "consumo_kwh": float(parts[4].split(":")[1].replace("kWh", ""))
                    }
                    # Guardar los datos en la base de datos local
                    save_data_to_db(data)
                    # Publicar los datos en MQTT
                    publish_message(topic, data)
                except (IndexError, ValueError, KeyError) as e:
                    print(f"Error al procesar la línea: {e}")
        time.sleep(1)  # Evitar sobrecargar el CPU

# Función para generar y publicar datos simulados
def simulate_data():
    while True:
        simulated_data = generate_simulated_data()
        print(f"Datos recibidos: {simulated_data}")
        # Guardar los datos en la base de datos local
        save_data_to_db(simulated_data)
        # Publicar los datos simulados en MQTT
        publish_message(topic, simulated_data)
        time.sleep(1)

# Función para gestionar la desconexión y reconexión de la cola de RabbitMQ
def manage_rabbitmq_connection():
    reconnect_rabbitmq()
    # Aquí puede ir la lógica para sincronizar los datos que no se enviaron cuando la conexión estaba perdida

# Crear y empezar los hilos
thread_serial = threading.Thread(target=read_from_serial)
thread_simulate = threading.Thread(target=simulate_data)
thread_rabbitmq = threading.Thread(target=manage_rabbitmq_connection)

thread_serial.start()
thread_simulate.start()
thread_rabbitmq.start()

# Esperar a que los hilos terminen (en este caso, el programa se mantiene en ejecución)
thread_serial.join()
thread_simulate.join()
thread_rabbitmq.join()
