import xml.etree.ElementTree as ET
from datetime import datetime
import rtree
import pyproj
import sumolib

json_data = {"type": "StructuredValue", "value": [
    {"_id": "6642127a58306f695e708dce", "entityId": "urn:ngsi-ld:Car:16005521", "entityType": "Car",
     "attrName": "speed", "attrType": "Float", "attrValue": 0, "recvTime": "2024-05-13T13:15:38.230Z"},
    {"_id": "6642127a6345ed2f80203615", "entityId": "urn:ngsi-ld:Car:127988955", "entityType": "Car",
     "attrName": "acceleration", "attrType": "Float", "attrValue": 0, "recvTime": "2024-05-13T13:15:38.246Z"},
    {"_id": "6642127a6345ed2f80203619", "entityId": "urn:ngsi-ld:Car:127988955", "entityType": "Car",
     "attrName": "confidence", "attrType": "Float", "attrValue": 52, "recvTime": "2024-05-13T13:15:38.246Z"},
    {"_id": "6642127a6345ed2f80203616", "entityId": "urn:ngsi-ld:Car:127988955", "entityType": "Car",
     "attrName": "detectedID", "attrType": "Text", "attrValue": 127988955, "recvTime": "2024-05-13T13:15:38.246Z"},
    {"_id": "6642127a6345ed2f8020361d", "entityId": "urn:ngsi-ld:Car:127988955", "entityType": "Car",
     "attrName": "hasDevices", "attrType": "Array", "attrValue": [], "recvTime": "2024-05-13T13:15:38.246Z"},
    {"_id": "6642127a6345ed2f80203618", "entityId": "urn:ngsi-ld:Car:127988955", "entityType": "Car",
     "attrName": "heading", "attrType": "Float", "attrValue": 0, "recvTime": "2024-05-13T13:15:38.246Z"},
    {"_id": "6642127a6345ed2f8020361a", "entityId": "urn:ngsi-ld:Car:127988955", "entityType": "Car",
     "attrName": "length", "attrType": "Float", "attrValue": 0, "recvTime": "2024-05-13T13:15:38.246Z"},
    {"_id": "6642127a6345ed2f8020361b", "entityId": "urn:ngsi-ld:Car:127988955", "entityType": "Car",
     "attrName": "location", "attrType": "geo:json",
     "attrValue": {"type": "Point", "coordinates": [-8.648414863, 40.632346937]},
     "recvTime": "2024-05-13T13:15:38.246Z"},
    {"_id": "6642127a6345ed2f80203617", "entityId": "urn:ngsi-ld:Car:127988955", "entityType": "Car",
     "attrName": "observedBy", "attrType": "Relationship", "attrValue": "urn:ngsi-ld:SlpCamera:033",
     "recvTime": "2024-05-13T13:15:38.246Z"},
    {"_id": "6642127a6345ed2f8020361c", "entityId": "urn:ngsi-ld:Car:127988955", "entityType": "Car",
     "attrName": "speed", "attrType": "Float", "attrValue": 0, "recvTime": "2024-05-13T13:15:38.246Z"}]}


def calculate_depart_time(start_time,recv_time):
    format = "%Y-%m-%dT%H:%M:%S.%fZ"

    start_dt = datetime.strptime(start_time, format)
    recv_dt = datetime.strptime(recv_time, format)

    # Calcular a diferença em segundos
    time_difference = (recv_dt - start_dt).total_seconds()

    return str(time_difference)


def parse_json_to_xml(start_time):
    root = ET.Element("routes", {
       "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/routes_file.xsd"
    })

    net = sumolib.net.readNet(
        "../Adapters/co_simulation/sumo_configuration/simple-map/UA.net.xml",
        withInternal=True)

    for item in json_data['value']:

        if item['attrName'] == 'location':
            coord = net.convertLonLat2XY(lon=-8.656930, lat =40.634771)
            edges = net.getNeighboringEdges(coord[0],coord[1]) # TODO: use traci
            print("aq",edges)



       # if item['entityType'] == 'Car':
       #     entity_elem = ET.SubElement(root, "vehicle", id=item['entityId'], type="vehicle.dodge.charger_police_2020",
       #                     depart=calculate_depart_time(start_time,item['recvTime']))
#
       # for attr_key in ['speed', 'acceleration', 'confidence', 'detectedID', 'hasDevices', 'heading', 'length',
       #                  'location', 'observedBy']:
#
       #     if attr_key in item:
       #         attr = item[attr_key]
       #         ET.SubElement(entity_elem, attr_key, type=attr['attrType']).text = str(attr['attrValue'])
#
       # #entity_elem.set('recvTime', item['recvTime'])

    tree = ET.ElementTree(root)
    with open("output.xml", "wb") as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
