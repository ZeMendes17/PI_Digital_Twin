import json
import os
import sys
import optparse
import threading

import sumolib

import traci
import paho.mqtt.client as mqtt

lista = {}


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

global step

def run():
    mqtt_client.subscribe("/teste")

    while True:
        traci.simulationStep()

        # update all the vehicles on the road
        for vehID in lista:
            # see if the vehicle is still in the simulation
            exists = traci.vehicle.getIDList().count(vehID)
            if exists: # update the vehicle's position
                print(lista[vehID])
                traci.vehicle.moveToXY(vehID, lista[vehID], 0, 0, angle=0, keepRoute=1)
                print(f"Veículo {vehID} existe no SUMO")
            else: # add the vehicle to the simulation
                traci.route.add("teste", [lista[vehID]])
                traci.vehicle.add(vehID, "teste", typeID="veh_passenger", depart="now", departSpeed=0, departLane="best")
                print(f"Veículo {vehID} adicionado no SUMO")


                


     #   pos = traci.vehicle.getPosition(vehicle_list[0])
     #   routeID = traci.vehicle.getRouteID(vehicle_list[0])
     #   typeID = traci.vehicle.getTypeID(vehicle_list[0])
     #   rout = traci.vehicle.getRoute(vehicle_list[0])
#
#
#
     #   if step == 10:
     #       traci.vehicle.add("teste", routeID, typeID, depart="now", departSpeed=0, departLane="best",
     #                        personCapacity=0, line="")

    # x,y = traci.vehicle.getPosition(vehicle_list[0]) #sumo vehicle position

    # log,lat = traci.simulation.convertGeo(x,y) #sumo position to lat,log

    # print(f'Vehicle: {vehicle_list[0]}, Position: {x},{y}, Lat: {lat}, Log: {log}')

    # x1,y1 = traci.simulation.convertGeo(log,lat, True ) #lat,log to sumo position

    # print(x1,y1)

    traci.close()
    sys.stdout.flush()


# nao ta a ser usada
def addOrUpdateCar(received):

    log, lat = received["data"]["location"]["lng"], received["data"]["location"]["lat"]
    vehID = received["vehicle"]
    x, y = traci.simulation.convertGeo(log, lat, True)
    nextEdge = traci.simulation.convertRoad(x, y)[0] # calcula a proxima aresta que o veículo vai passar de acordo com as coordenadas recebidas

    # add or update the vehicle
    lista[vehID] = nextEdge
    if vehID in lista:
        print(f"Vehicle {vehID} already exists in the list")
    else:
        print(f"Vehicle {vehID} does not exist in the list")

    try:

        traci.vehicle.getPosition(vehID) # se o veículo não existir, vai dar erro e passa para o except
        print(f"Veículo {received['vehicle']} existe no SUMO")
        print("proxima aresta", nextEdge)
        #oldRoute = traci.vehicle.getRoute(vehID) #rota é uma lista de arestas que o veículo vai passar
        #print(f"Rota do veículo {received['vehicle']}:", oldRoute)
        #updatedRoute = oldRoute.append(nextEdge) # adiciona a nova aresta na rota do veículo
        #print(f"Rota atualizada do veículo {received['vehicle']}:", updatedRoute)
        traci.vehicle.moveToXY(vehID, nextEdge, 0, 0, angle=0, keepRoute=1) # move o veículo para a nova aresta

    except:
        print(f"Veículo {received['vehicle']} não existe no SUMO")
        traci.route.add("teste", [nextEdge]) # adiciona a rota do veículo contendo apenas a próxima aresta

        traci.vehicle.add(vehID, "teste", typeID="veh_passenger", depart="now", departSpeed=0, departLane="best")
        print(f"Veículo {received['vehicle']} adicionado no SUMO")
        print("rota", traci.vehicle.getRoute(vehID))

def addOrUpdateCarToList(received):
    log, lat = received["data"]["location"]["lng"], received["data"]["location"]["lat"]
    vehID = received["vehicle"]
    x, y = traci.simulation.convertGeo(log, lat, True)
    nextEdge = traci.simulation.convertRoad(x, y)[0]  # calcula a proxima aresta que o veículo vai passar de acordo com as coordenadas recebidas

    # add or update the vehicle
    if vehID in lista:
        print(f"Vehicle {vehID} already exists in the list")
    else:
        print(f"Vehicle {vehID} does not exist in the list")

    lista[vehID] = nextEdge


def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker com código de resultado {rc}")


def on_publish(client, userdata, mid):
    print("Mensagem publicada com sucesso")


def on_message(client, userdata, msg):
    received = json.loads(msg.payload.decode())
    print(f"Received `{received}` from `{msg.topic}` topic")
    addOrUpdateCarToList(received)


if __name__ == "__main__":
    options = get_options()
    if options.nogui:
        sumoBinary = sumolib.checkBinary('sumo')
    else:
        sumoBinary = sumolib.checkBinary('sumo-gui')

    # Inicia a conexão MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()  # Inicia o loop de eventos MQTT em uma thread separada

    # Inicia o SUMO em uma thread separada
    sumo_thread = threading.Thread(target=traci.start, args=[
        [sumoBinary, "-c", "../sumo_netWork/osm.sumocfg", "--tripinfo-output", "tripinfo.xml"]])
    sumo_thread.start()

    # Executa a função run (controle do SUMO) após o início do SUMO
    sumo_thread.join()  # Aguarda até que o SUMO esteja pronto
    run()
