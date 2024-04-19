import json
import random
import optparse
import threading
import time

import sumolib
import traci
import sys
import os

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(os.path.dirname(__file__), "radar.json")
from coord_distance import calculate_bearing


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


global step
lista = {}
simulated_vehicles = {}

net = sumolib.net.readNet(
        "../Adapters/co_simulation/sumo_configuration/simple-map/aveiro.net.xml",
        withInternal=True)  # Carrega a rede do SUMO atraves do sumolib para acesso estatico


def run():
    step = 0
    while True:

        traci.simulationStep()
        step += 1

        simulation_time = traci.simulation.getTime()
        vehicles = traci.vehicle.getIDList()
        vehicle_type = traci.vehicletype.getIDList()

        data = {"vehicle": {"quantity": len(vehicles), "ids": vehicles, "types": vehicle_type}, "time": simulation_time}
        publish.single("/cars", payload=json.dumps(data), hostname="localhost", port=1883)

        if len(simulated_vehicles) > 0:
            for vehicle_id in simulated_vehicles:
                if vehicle_id in traci.vehicle.getIDList():
                    checkDestination(vehicle_id, simulated_vehicles[vehicle_id])

    traci.close()
    sys.stdout.flush()


# Function to check if vehicle has reached destination
def checkDestination(vehicle_id, destination_coordinates):
    global simulated_vehicles
    # Check if vehicle is in the list of simulated vehicles and is still in the simulation
    if vehicle_id in simulated_vehicles and vehicle_id in traci.vehicle.getIDList():
        vehicle_position = traci.vehicle.getPosition(vehicle_id)
        if vehicle_position is not None:
            print("Vehicle {} is at position: {}".format(vehicle_id, vehicle_position))
            print("Destination coordinates: {}".format(destination_coordinates))
            distance_to_destination = traci.simulation.getDistance2D(float(vehicle_position[0]),
                                                                     float(vehicle_position[1]),
                                                                     float(destination_coordinates[0]),
                                                                     float(destination_coordinates[1]))
            if distance_to_destination < 5:  # 5 meters from destination
                traci.vehicle.stop(vehicle_id)
                simulated_vehicles.pop(vehicle_id, None)
                print("Vehicle {} has reached its destination.".format(vehicle_id))
    else:
        print("Vehicle {} not found in the list of simulated vehicles.".format(vehicle_id))


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
        routeEdges = traci.route.getEdges(
            routeName)  # agora percorremos isso, e sempre que iniciar com : ou _ usamos o getOutgoingEdges para subsituir por um edge que começa ali
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
                          typeID="vehicle.audi.a2", depart=traci.simulation.getTime() + 2, departSpeed=0,
                          departLane="best")
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
                          typeID="vehicle.audi.a2", depart=traci.simulation.getTime() + 5, departSpeed=0,
                          departLane="best")

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

    def decodeRealData(data):
        return json.loads(data.decode('utf-8'))


def endSimulation():
    traci.close()
    sys.stdout.flush()


def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker com código de resultado {rc}")

def on_connect_real_data(client, userdata, flags, reason_code, properties):
    print("Connected with result code " + str(reason_code))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("p35/jetson/radar-plus")  


def on_publish(client, userdata, mid):
    print("Mensagem publicada com sucesso (simulation)")


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
        print(msg.payload)
        payload = msg.payload
        addSimulatedCar(payload)

    if topic == "/endSimulation":
        print("Ending simulation...")
        endSimulation()
        print("Simulation ended")


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
    mqtt_client.subscribe("/realDatateste") # vira o topico real
    mqtt_client.subscribe("/addRandomTraffic")
    mqtt_client.subscribe("/addSimulatedCar")
    mqtt_client.subscribe("/endSimulation")

    mqtt_client.loop_start()  # Inicia o loop de eventos MQTT em uma thread separada

    # Inicia o SUMO em uma thread separada

    # Aveiro sumo network
    sumo_thread = threading.Thread(target=traci.start, args=[
        [sumoBinary, "-c", "../Adapters/co_simulation/sumo_configuration/simple-map/simple-map.sumocfg",
         "--tripinfo-output",
         "tripinfo.xml",
         "--quit-on-end"
         ]])

    # Simple sumo network
    # sumo_thread = threading.Thread(target=traci.start, args=[
    #     [sumoBinary, "-c", "../simple_sumo_network/osm.sumocfg", "--tripinfo-output", "simple_tripinfo.xml"]])
    sumo_thread.start()
    # Executa a função run (controle do SUMO) após o início do SUMO
    sumo_thread.join()  # Aguarda até que o SUMO esteja pronto

     # Inicia a conexão MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.subscribe("/realDatateste")
    mqtt_client.subscribe("/addRandomTraffic")
    mqtt_client.subscribe("/addSimulatedCar")
    mqtt_client.subscribe("/endSimulation")

    mqtt_thread = threading.Thread(target=mqtt_client.loop_start)
    mqtt_thread.start()


    realData_mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    realData_mqtt_client.on_connect = on_connect_real_data
    realData_mqtt_client.on_message = on_message
    realData_mqtt_client.connect("atcll-data.nap.av.it.pt", 1884)

    realData_mqtt_client.loop_start()

    #sumolib para dados estaticos da rede e traci para dados dinamicos da simulação
    #teste = net.getEdge("-1545").getLanes()
    #for i in teste:
    #    print(i.getPermissions())

    run()
