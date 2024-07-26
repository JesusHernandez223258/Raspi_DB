import os
import json
import paho.mqtt.client as mqtt

mqttUrl ="52.55.82.224"
options = {
    'username': "saul",
    'password': "PiWeb223"
}

def connect_to_mqtt():
    client = mqtt.Client()
    client.username_pw_set(options['username'], options['password'])

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Conectado al broker MQTT.")
        else:
            print(f"Error de conexión con código {rc}")

    def on_disconnect(client, userdata, rc):
        print(f"Desconectado del broker MQTT con código {rc}")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(mqttUrl, 1883, 60)  # 60 segundos de timeout
        print(f"Conectado a rabbit")
    except Exception as e:
        print(f"Error al conectar al broker MQTT: {e}")
        raise
    return client


def publish_message(topic, message):
    try:
        print(f"Publicando en el tema {topic} con el mensaje: {message}")
        json_message = json.dumps(message)
        print(f"Mensaje JSON serializado: {json_message}")
        client = connect_to_mqtt()
        client.publish(topic, json_message)
        client.disconnect()
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el JSON: {e}")
    except Exception as e:
        print(f"Error al publicar el mensaje: {e}")

