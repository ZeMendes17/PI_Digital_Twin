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

    step = 0
    while True:



        if len(lista) > 0:
            for key in lista.keys():
                addOrUpdateCar({"vehicle": key, "data": lista[key]}) # para nao desregular os steps do sumo, a função addOrUpdateCar é chamada aqui




        traci.simulationStep()
        
        # # get cars list in the simulation
        # vehicle_list = traci.vehicle.getIDList()
        
        # for vehicle in vehicle_list:
        #     x, y = traci.vehicle.getPosition(vehicle)
        #     log, lat = traci.simulation.convertGeo(x, y)
        #     print(f'{{"lat": {lat}, "lng": {log}}},')


        step += 1

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


def addOrUpdateCar(received):
    log, lat = received["data"]["location"]["lng"], received["data"]["location"]["lat"]
    vehID = received["vehicle"]
    x, y = traci.simulation.convertGeo(log, lat, True)
    nextEdge = traci.simulation.convertRoad(log,lat,True)[0] # calcula a proxima aresta que o veículo vai passar de acordo com as coordenadas recebidas
    allCars = traci.vehicle.getIDList()
    print("next", nextEdge)

    if vehID in allCars: # Verifica se o veículo já existe
        print(traci.vehicle.getRoadID(vehID))
        if traci.vehicle.getRoadID(vehID) == nextEdge or nextEdge.startswith(":cluster") or "_" in nextEdge:
            traci.vehicle.moveToXY(vehID, nextEdge, 0, x, y, keepRoute=1) # se a proxima for a mesma, cluster ou de junção, move com moveTOXY


        else:
            traci.vehicle.changeTarget(vehID, nextEdge) # se a proxima aresta for diferente, muda a rota
            print("mudou", traci.vehicle.getRoute(vehID))


    else: # Adiciona um novo veículo
        traci.route.add(routeID=("route_" + vehID), edges=[nextEdge]) # adiciona uma rota para o veículo
        print("definiu rota")
        traci.vehicle.add(vehID, routeID=("route_" + vehID), typeID="vehicle.audi.a2", depart="now", departSpeed=0, departLane="best",)
        print(traci.vehicle.getRoute(vehID))
        print("aq", traci.vehicle.getRoadID(vehID))
        print("adicionado")


def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker com código de resultado {rc}")


def on_publish(client, userdata, mid):
    print("Mensagem publicada com sucesso")


def on_message(client, userdata, msg):
    received = json.loads(msg.payload.decode())
    #print(f"Received `{received}` from `{msg.topic}` topic")
    lista[received["vehicle"]] = received["data"]





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
    
    # Aveiro sumo network
    sumo_thread = threading.Thread(target=traci.start, args=[
        [sumoBinary, "-c", "../co_simulation/ruadapega.sumocfg", "--tripinfo-output", "tripinfo.xml"]])

    # Simple sumo network
    # sumo_thread = threading.Thread(target=traci.start, args=[
    #     [sumoBinary, "-c", "../simple_sumo_network/osm.sumocfg", "--tripinfo-output", "simple_tripinfo.xml"]])
    sumo_thread.start()

    # Executa a função run (controle do SUMO) após o início do SUMO
    sumo_thread.join()  # Aguarda até que o SUMO esteja pronto

    
    run()
