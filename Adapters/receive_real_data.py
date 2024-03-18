import paho.mqtt.client as mqtt
import json
import pprint

vehicles = {}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected with result code " + str(reason_code))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("jetson/radar-plus")      # 'jetson/radar/+/1' -> will subscribe to both 'jetson/radar/traffic/1' and jetson/radar/count/1


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    info = json.loads(msg.payload.decode('utf-8'))
    
    print('Topic: ' + msg.topic)
    pprint.pprint(info)

    #### ADDED
    vehicle_id = info["objectID"]
    if vehicle_id not in vehicles:
        vehicles[vehicle_id] = [{"lat": info["latitude"]
                                ,"lng": info["longitude"]}]
    else:
        vehicles[vehicle_id].append({"lat": info["latitude"] ,"lng": info["longitude"]})

    if len(vehicles[vehicle_id]) == 10:
        pprint.pprint(vehicles[vehicle_id])
    ####
    print('\n')

    client.publish('dummy-info', json.dumps({
        "speed": info['speed']
    }))


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message


client.connect("atcll-p1-jetson.nap.av.it.pt", 1883, 60) # base => p35

client.publish('dummy', 'Connected')

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
