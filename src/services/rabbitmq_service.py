import os
import json
import paho.mqtt.client as mqtt

mqttUrl = os.getenv('MQTT_BROKER')
options = {
    'username': os.getenv('MQTT_USERNAME'),
    'password': os.getenv('MQTT_PASSWORD')
}

def connect_to_mqtt(topic):
    try:
        client = mqtt.Client()
        client.username_pw_set(options['username'], options['password'])
        client.connect(mqttUrl)

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Conectado al broker MQTT. Suscrito al tema: {topic}")
                client.subscribe(topic, qos=1)
            else:
                print(f"Error de conexión con código {rc}")

        client.on_connect = on_connect
        return client
    except Exception as e:
        print(f"Error en el consumidor: {e}")

def publish_message(topic, message):
    try:
        client = mqtt.Client()
        client.username_pw_set(options['username'], options['password'])
        client.connect(mqttUrl)
        client.publish(topic, json.dumps(message), qos=1)
        client.disconnect()
    except Exception as e:
        print(f"Error al publicar el mensaje: {e}")
