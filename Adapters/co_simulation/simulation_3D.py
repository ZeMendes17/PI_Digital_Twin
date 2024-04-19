# ==================================================================================================
# -- imports ---------------------------------------------------------------------------------------
# ==================================================================================================

import argparse
import logging
import random
import time
import json
import os
import sys
import optparse
import threading
import sumolib
import traci
import paho.mqtt.client as mqtt

file_path = os.path.join(os.path.dirname(__file__), "radar.json")
from coord_distance import calculate_bearing


# ==================================================================================================
# -- find carla module -----------------------------------------------------------------------------
# ==================================================================================================

import glob
import os
import sys

try:
    sys.path.append(
        glob.glob('/home/pi-digitaltwin/Desktop/CARLA/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' %
                  (sys.version_info.major, sys.version_info.minor,
                   'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


# ==================================================================================================
# -- sumo integration imports ----------------------------------------------------------------------
# ==================================================================================================

from sumo_integration.sumo_simulation import SumoSimulation  # pylint: disable=wrong-import-position
from sumo_integration.carla_simulation import CarlaSimulation  # pylint: disable=wrong-import-position
from modules.simulation_synchronization import SimulationSynchronization


net = sumolib.net.readNet(
    "../Adapters/co_simulation/sumo_configuration/simple-map/aveiro.net.xml",
    withInternal=True)  # Carrega a rede do SUMO atraves do sumolib para acesso estatico



def synchronization_loop(args):
    """
    Entry point for sumo-carla co-simulation.
    """
    sumo_simulation = SumoSimulation(args.sumo_cfg_file, args.step_length, args.sumo_host,
                                     args.sumo_port, args.sumo_gui, args.client_order)
    carla_simulation = CarlaSimulation(args.carla_host, args.carla_port, args.step_length)

    synchronization = SimulationSynchronization(sumo_simulation, carla_simulation, args.tls_manager,
                                                args.sync_vehicle_color, args.sync_vehicle_lights)
    try:
        while True:

            start = time.time()

            synchronization.tick()

            end = time.time()
            elapsed = end - start
            if elapsed < args.step_length:
                time.sleep(args.step_length - elapsed)

    except KeyboardInterrupt:
        logging.info('Cancelled by user.')

    finally:
        logging.info('Cleaning synchronization')

        synchronization.close()




########### SUMOSUBSCRIBE

lista = {}
count = 0
simulated_vehicles = {}

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options



def addOrUpdateCar(received):
    log, lat, heading = received["data"]["location"]["lng"], received["data"]["location"]["lat"], received["data"]["heading"]
    # if the heading is positive it is directed to the sensor, if it is negative it is directed away from the sensor
    # get the sensor information from radar.json
    f = open("radar.json", "r")
    radar_data = json.load(f)
    radar = radar_data[0]
    # get the angle from the sensor to the vehicle
    angle = calculate_bearing((radar['coord']['lat'], radar['coord']['lng']), (lat, log))
    if radar['angle_type'] == 0:
        if 0 <= angle <= 90 or 270 <= angle <= 360:
            if heading < 0:
                nextEdge = radar['lanes']['near']
            else:
                nextEdge = radar['lanes']['far']
        else:
            if heading < 0:
                nextEdge = radar['lanes']['far']
            else:
                nextEdge = radar['lanes']['near']
    f.close()
    
    
    vehID = received["vehicle"]
    x, y = traci.simulation.convertGeo(log, lat, True)
    # nextEdge = traci.simulation.convertRoad(x,y, False, "passenger")[0] # calcula a proxima aresta que o veículo vai passar de acordo com as coordenadas recebidas
    nextEdge = str(nextEdge)
    allCars = traci.vehicle.getIDList()
    print("next", nextEdge)

    if vehID in allCars: # Verifica se o veículo já existe
        print(traci.vehicle.getRoadID(vehID))
        if traci.vehicle.getRoadID(vehID) == nextEdge or nextEdge.startswith(":cluster") or "_" in nextEdge:
            # actualane = traci.vehicle.getLaneID(vehID)
            # traci.vehicle.moveToXY(vehID, nextEdge, actualane, x, y, keepRoute=1) # se a proxima for a mesma, cluster ou de junção, move com moveTOXY
            # Change speed
            traci.vehicle.setSpeed(vehID, 10)
            global count
            if count >= 15 :
                traci.vehicle.setSpeed(vehID, 10)
            elif count > 10:
                traci.vehicle.setSpeed(vehID, 0)

            count += 1
            print(count)

        else:
            traci.vehicle.changeTarget(vehID, nextEdge) # se a proxima aresta for diferente, muda a rota
            print("mudou", traci.vehicle.getRoute(vehID))


    else: # Adiciona um novo veículo
        traci.route.add(routeID=("route_" + vehID), edges=[nextEdge]) # adiciona uma rota para o veículo
        traci.vehicle.add(vehID, routeID=("route_" + vehID), typeID="vehicle.audi.a2", depart="now", departSpeed=0, departLane="best",)
        traci.vehicle.moveToXY(vehID, nextEdge, 0, x, y, keepRoute=1) # se a proxima for a mesma, cluster ou de junção, move com moveTOXY
        print(traci.vehicle.getRoute(vehID))
        # print("aq", traci.vehicle.getRoadID(vehID))
        print("adicionado")

def addOrUpdateRealCar(received):
    print("received", received)
    log, lat, heading = received["longitude"], received["latitude"], received["heading"]
    print("log: {}, lat: {}, heading: {}".format(log, lat, heading))
    # if the heading is positive it is directed to the sensor, if it is negative it is directed away from the sensor
    # get the sensor information from radar.json
    with open(file_path, "r") as f:
        data = json.load(f)
        radar = data[1]
        # get the angle from the sensor to the vehicle
        angle = calculate_bearing((radar['coord']['lat'], radar['coord']['lng']), (lat, log))
        if radar['angle_type'] == 0:
            if 0 <= angle <= 90 or 270 <= angle <= 360:
                if heading < 0:
                    nextEdge = radar['lanes']['near']
                else:
                    nextEdge = radar['lanes']['far']

            else:
                if heading < 0:
                    nextEdge = radar['lanes']['far']
                else:
                    nextEdge = radar['lanes']['near']

        elif radar['angle_type'] == 1:
            if 0 <= angle <= 90 or 270 <= angle <= 360:
                if heading < 0:
                    nextEdge = radar['lanes']['far']
                else:
                    nextEdge = radar['lanes']['near']

            else:
                if heading < 0:
                    nextEdge = radar['lanes']['near']
                else:
                    nextEdge = radar['lanes']['far']
        f.close()

    vehID = str(received["objectID"])
    x, y = net.convertLonLat2XY(log, lat)  # Converte as coordenadas para o sistema de coordenadas do SUMO
    nextEdge = str(nextEdge)
    allCars = traci.vehicle.getIDList()
    print("next", nextEdge)

    if vehID in allCars:
        print(traci.vehicle.getRoadID(vehID))
        if traci.vehicle.getRoadID(vehID) == nextEdge or nextEdge.startswith(":cluster") or "_" in nextEdge:

            new_speed = received["speed"]
            traci.vehicle.setSpeed(vehID, new_speed)
        else:
            traci.vehicle.changeTarget(vehID, nextEdge)  # se a proxima aresta for diferente, muda a rota
            print("mudou", traci.vehicle.getRoute(vehID))


    else:  # Adiciona um novo veículo
        traci.route.add(routeID=("route_" + vehID), edges=[nextEdge])  # adiciona uma rota para o veículo
        traci.vehicle.add(vehID, routeID=("route_" + vehID), typeID="vehicle.audi.a2", depart=traci.simulation.getTime() + 0.5, departSpeed=0,
                          departLane="best")
        traci.vehicle.moveToXY(vehID, nextEdge, 0, x, y,
                               keepRoute=1)  # se a proxima for a mesma, cluster ou de junção, move com moveTOXY
        print(traci.vehicle.getRoute(vehID))
        print("adicionado")


def addSimulatedCar(received):
    print(type(received))
    data = json.loads(received.decode('utf-8'))
    print("data", data.keys())

    if data.keys() == {"start", "end"}:
        logI, latI = data["start"]["lng"], data["start"]["lat"]
        logE, latE = data["end"]["lng"], data["end"]["lat"]


        Start = traci.simulation.convertRoad(float(logI), float(latI), isGeo=True, vClass="passenger")
        End = traci.simulation.convertRoad(float(logE), float(latE), isGeo=True, vClass="passenger")

        print("Start", Start)
        print("End", End)
        ts = str(time.time_ns())
        routeName = "route_simulated{}".format(ts)

        # Store destination coordinates
        destination_coordinates = End

        traci.route.add(routeName, [Start[0], End[0]])
        routeEdges = traci.route.getEdges(routeName) # agora percorremos isso, e sempre que iniciar com : ou _ usamos o getOutgoingEdges para subsituir por um edge que começa ali
        finalEdges = []

        for edge in routeEdges:
            if edge.startswith(":") or "_" in edge:
                print("edge", edge)
                outgoingEdges = net.getEdge(edge).getOutgoing()
                print("outgoing", outgoingEdges)

                for i in outgoingEdges:
                    edgeIndex = routeEdges.index(edge)
                    if edgeIndex == 0:
                        finalEdges.append(str(i.getID()))
                        break
                    finalEdges.append(str(i.getID()))
                    break
            else:
                finalEdges.append(str(edge))


        finalRouteName = "route_simulated{}".format(str(time.time_ns()))
        traci.route.add(finalRouteName, finalEdges)
        traci.vehicle.add(vehID="simulated{}".format(finalRouteName), routeID=finalRouteName,
                          typeID="vehicle.audi.a2", depart=traci.simulation.getTime() + 2, departSpeed=0, departLane="best")
        print("Veículo adicionado com informações de início e fim", "simulated{}".format(ts))

        # Store simulated vehicle ID and its destination coordinates
       # simulated_vehicle_id = traci.vehicle.getIDList()[-1]
       # simulated_vehicles[simulated_vehicle_id] = destination_coordinates
       # print("simulated_vehicles", simulated_vehicles)

        # make the car move to XY
        x, y = net.convertLonLat2XY(logI, latI)
        traci.vehicle.moveToXY("simulated{}".format(finalRouteName), Start[0], 0, x, y, keepRoute=1)
        print("moveToXY", "simulated{}".format(ts))



    elif data.keys() == {"start"}:
        allowedEdges = [i.getID() for i in net.getEdges() if "driving" in i.getType()]
        randomEdge = random.choice(allowedEdges)
        print("random", randomEdge)
        logI, latI = data["start"]["lng"], data["start"]["lat"]

        print("logI: {}, latI: {}".format(logI, latI))

        Start = traci.simulation.convertRoad(float(logI), float(latI), isGeo=True, vClass="passenger")

        if Start[0].startswith(":") or "_" in Start[0]:
            outgoingEdges = net.getEdge(Start[0]).getOutgoing()
            nextEdge = next(iter(outgoingEdges)).getID()

            ts = str(time.time_ns())
            routeName = "route_simulated{}".format(ts)
            traci.route.add(routeName, [nextEdge, randomEdge])


        else:
            ts = str(time.time_ns())
            routeName = "route_simulated{}".format(ts)
            traci.route.add(routeName, [Start[0], randomEdge])

        print("edgees:", traci.route.getEdges(routeName))
        # Store destination coordinates
        destination_coordinates = randomEdge
        traci.vehicle.add(vehID="simulated{}".format(ts), routeID=routeName,
                              typeID="vehicle.audi.a2", depart=traci.simulation.getTime() + 5, departSpeed=0, departLane="best")

        # make the car move to XY
        x, y = net.convertLonLat2XY(logI, latI)
        traci.vehicle.moveToXY("simulated{}".format(ts), Start[0], 0, x, y, keepRoute=1)
        print("moveToXY", "simulated{}".format(ts))




        
        # Store simulated vehicle ID and its destination coordinates
        #simulated_vehicle_id = traci.vehicle.getIDList()[-1]
        #simulated_vehicles[simulated_vehicle_id] = destination_coordinates
        
        return "Veículo adicionado com informações de início"

    elif data.keys() == {"end"}:
        allowedEdges = [i.getID() for i in net.getEdges() if "driving" in i.getType()]
        randomEdge = random.choice(allowedEdges)
        logE, latE = data["end"]["lng"], data["end"]["lat"]

        print("logE: {}, latE: {}".format(logE, latE))

        End = traci.simulation.convertRoad(float(logE), float(latE), isGeo=True, vClass="passenger")

        print("End", End)
        ts = str(time.time_ns())
        traci.route.add("route_simulated{}".format(ts), [randomEdge, End[0]])

        # Store destination coordinates
        destination_coordinates = End


        traci.vehicle.add(vehID="simulated{}".format(ts), routeID="route_simulated{}".format(ts),
                          typeID="vehicle.audi.a2", depart="now", departSpeed=0, departLane="best")
        
        # Store simulated vehicle ID and its destination coordinates
        simulated_vehicle_id = traci.vehicle.getIDList()[-1]
        simulated_vehicles[simulated_vehicle_id] = destination_coordinates

        return "Veículo adicionado com informações de fim"

def addRandomTraffic(QtdCars):
    allowedEdges = [i.getID() for i in net.getEdges() if "driving" in i.getType()]
    types = traci.vehicletype.getIDList()
    print(types)
    print(allowedEdges)
    if len(allowedEdges) != 0:

        for count in range(QtdCars):
            routeID = "route_{}".format(time.time_ns())
            vehicle_id = "random_{}".format(time.time_ns())
            typeID = random.choice(types)
            route = traci.simulation.findRoute(random.choice(allowedEdges), random.choice(allowedEdges), typeID)
            
            if route.edges:
                traci.route.add(routeID, route.edges)
                traci.vehicle.add(vehicle_id, routeID, typeID, depart="now", departSpeed=0,
                              departLane="best", )

def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker com código de resultado {rc}")

def on_connect_real_data(client, userdata, flags, reason_code, properties):
    print("Connected with result code " + str(reason_code))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("p35/jetson/radar-plus")  


def on_publish(client, userdata, mid):
    print("Mensagem publicada com sucesso")


def on_message(client, userdata, msg):
    topic = msg.topic
    print(topic)
    if topic == "p35/jetson/radar-plus":
        print("REAL DATA")
        payload = json.loads(msg.payload)
        addOrUpdateRealCar(payload)
    if topic == "/addRandomTraffic":
        payload = json.loads(msg.payload)
        try:
            addRandomTraffic(int(payload))
        except Exception as e:
            print(e)
    if topic == "/addSimulatedCar":
        print("entrou", topic)
        payload = msg.payload
        addSimulatedCar(payload)


def synchronization_loop_wrapper(arguments):
    synchronization_loop(arguments)

if __name__ == "__main__":
    class StaticArguments:
        def __init__(self):
            self.sumo_cfg_file = "../Adapters/co_simulation/sumo_configuration/simple-map/simple-map.sumocfg"
            self.carla_host = '127.0.0.1'
            self.carla_port = 2000
            self.sumo_host = None
            self.sumo_port = None
            self.sumo_gui = True
            self.step_length = 0.05
            self.client_order = 1
            self.sync_vehicle_lights = False
            self.sync_vehicle_color = False
            self.sync_vehicle_all = False
            self.tls_manager = 'carla'
            self.debug = False


    # Cria uma instância dos argumentos estáticos
    arguments = StaticArguments()

    if arguments.sync_vehicle_all is True:
        arguments.sync_vehicle_lights = True
        arguments.sync_vehicle_color = True

    if arguments.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    print("teste")
    synchronization_thread = threading.Thread(target=synchronization_loop_wrapper, args=[arguments])
    synchronization_thread.start()

    
    print("teste2")
    # Inicia a conexão MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.subscribe("/realDatateste")
    mqtt_client.subscribe("/addRandomTraffic")
    mqtt_client.subscribe("/addSimulatedCar")
    mqtt_client.loop_start()  # Inicia o loop de eventos MQTT em uma thread separada

    
    mqtt_thread = threading.Thread(target=mqtt_client.loop_start)
    mqtt_thread.start()


    realData_mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    realData_mqtt_client.on_connect = on_connect_real_data
    realData_mqtt_client.on_message = on_message
    realData_mqtt_client.connect("atcll-data.nap.av.it.pt", 1884)

    realData_mqtt_client.loop_start()
