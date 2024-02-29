import os
import sys
import optparse
import threading
from sumolib import checkBinary
import traci
import paho.mqtt.client as mqtt

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

def run():

    while traci.simulation.getMinExpectedNumber() > 0:  # Enquanto houver carros na simulação
        traci.simulationStep()  # Avança a simulação em um passo
        vehicle_list = traci.vehicle.getIDList()
        simulation_time = traci.simulation.getCurrentTime()
        message = f'Simulation_time: {simulation_time}, Vehicle_List: {vehicle_list}'

        mqtt_client.publish("/info", message)




    traci.close()
    sys.stdout.flush()

def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker com código de resultado {rc}")

def on_publish(client, userdata, mid):
    print("Mensagem publicada com sucesso")

if __name__ == "__main__":
    options = get_options()
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # Inicia a conexão MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()  # Inicia o loop de eventos MQTT em uma thread separada

    # Inicia o SUMO em uma thread separada
    sumo_thread = threading.Thread(target=traci.start, args=[[sumoBinary, "-c", "../sumo_netWork/osm.sumocfg", "--tripinfo-output", "tripinfo.xml"]])
    sumo_thread.start()

    # Executa a função run (controle do SUMO) após o início do SUMO
    sumo_thread.join()  # Aguarda até que o SUMO esteja pronto
    run()
