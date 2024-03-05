import json
import os
import sys
import optparse
import threading
import time

from sumolib import checkBinary
import traci
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker com código de resultado {rc}")


def on_publish(client, userdata, mid):
    print(f"Mensagem publicada com sucesso")


def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


if __name__ == "__main__":
    # Inicia a conexão MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()  # Inicia o loop de eventos MQTT em uma thread separada

    coordenadas = [
        {"lat": 40.6361250091032, "lng": -8.659596064875444},
        {"lat": 40.63614421690061, "lng": -8.659584022192302},
        {"lat": 40.63617451402699, "lng": -8.659565026833864},
        {"lat": 40.63621796381109, "lng": -8.659537747677366},
        {"lat": 40.636280362615636, "lng": -8.6594983934419},
        {"lat": 40.63635442498533, "lng": -8.659451569633564},
        {"lat": 40.636445762348984, "lng": -8.65939350430772},
        {"lat": 40.636548697617705, "lng": -8.659328563126143},
        {"lat": 40.636663397520344, "lng": -8.659257355031114},
        {"lat": 40.63677383776296, "lng": -8.659189109605107},
        {"lat": 40.63688392296575, "lng": -8.659121026816775},
        {"lat": 40.636996428455866, "lng": -8.659051446928977},
        {"lat": 40.637109249752726, "lng": -8.65898167146447},
        {"lat": 40.63722340802476, "lng": -8.658911068865555},
        {"lat": 40.637333804417715, "lng": -8.658842792590345},
        {"lat": 40.637449686271246, "lng": -8.658771123479337},
        {"lat": 40.63756888953621, "lng": -8.658697399894125}
    ]

    for coordenada in coordenadas:

        data = {
            "vehicle": "VEICULOTEST",
            "data": {
                "location": {
                    "lat": coordenada["lat"],
                    "lng": coordenada["lng"]
                },
                "speed": 43
            }



        }

        payload = json.dumps(data)
        mqtt_client.publish("/teste", payload)
        time.sleep(0.8)

