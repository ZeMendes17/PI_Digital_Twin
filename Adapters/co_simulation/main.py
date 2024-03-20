# ==================================================================================================
# -- imports ---------------------------------------------------------------------------------------
# ==================================================================================================

import argparse
import logging
import time
import json
import os
import sys
import optparse
import threading
import sumolib
import traci
import paho.mqtt.client as mqtt

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
        mqtt_client.subscribe("/teste")
        while True:
            

            # if traci.simulation.getTime() == 10:
            #     traci.route.add(routeID="route_0", edges=["-478", "-462"])
            #     traci.vehicle.add(vehID="car_0", routeID="route_0", typeID="vehicle.audi.a2", depart="now", departSpeed=0, departLane="best")
            
            if len(lista) > 0:
                for key in lista.keys():
                    addOrUpdateCar({"vehicle": key, "data": lista[key]})
            
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
        
        


        step += 1

     

    traci.close()
    sys.stdout.flush()


def addOrUpdateCar(received):
    log, lat, heading = received["data"]["location"]["lng"], received["data"]["location"]["lat"], received["data"]["heading"]
    # if the heading is positive it is directed to the sensor, if it is negative it is directed away from the sensor
    # get the sensor information from radar.json
    f = open("../radar.json", "r")
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


def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker com código de resultado {rc}")


def on_publish(client, userdata, mid):
    print("Mensagem publicada com sucesso")


def on_message(client, userdata, msg):
    received = json.loads(msg.payload.decode())
    #print(f"Received `{received}` from `{msg.topic}` topic")
    lista[received["vehicle"]] = received["data"]

def synchronization_loop_wrapper(arguments):
    synchronization_loop(arguments)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('sumo_cfg_file', type=str, help='sumo configuration file')
    argparser.add_argument('--carla-host',
                           metavar='H',
                           default='127.0.0.1',
                           help='IP of the carla host server (default: 127.0.0.1)')
    argparser.add_argument('--carla-port',
                           metavar='P',
                           default=2000,
                           type=int,
                           help='TCP port to listen to (default: 2000)')
    argparser.add_argument('--sumo-host',
                           metavar='H',
                           default=None,
                           help='IP of the sumo host server (default: 127.0.0.1)')
    argparser.add_argument('--sumo-port',
                           metavar='P',
                           default=None,
                           type=int,
                           help='TCP port to listen to (default: 8813)')
    argparser.add_argument('--sumo-gui', action='store_true', help='run the gui version of sumo')
    argparser.add_argument('--step-length',
                           default=0.05,
                           type=float,
                           help='set fixed delta seconds (default: 0.05s)')
    argparser.add_argument('--client-order',
                           metavar='TRACI_CLIENT_ORDER',
                           default=1,
                           type=int,
                           help='client order number for the co-simulation TraCI connection (default: 1)')
    argparser.add_argument('--sync-vehicle-lights',
                           action='store_true',
                           help='synchronize vehicle lights state (default: False)')
    argparser.add_argument('--sync-vehicle-color',
                           action='store_true',
                           help='synchronize vehicle color (default: False)')
    argparser.add_argument('--sync-vehicle-all',
                           action='store_true',
                           help='synchronize all vehicle properties (default: False)')
    argparser.add_argument('--tls-manager',
                           type=str,
                           choices=['none', 'sumo', 'carla'],
                           help="select traffic light manager (default: none)",
                           default='none')
    argparser.add_argument('--debug', action='store_true', help='enable debug messages')
    arguments = argparser.parse_args()

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
    mqtt_client.loop_start()  # Inicia o loop de eventos MQTT em uma thread separada

    

