import json

class ReceiveData:
    """
    This class is responsible for receiving data from the sensors,
    storing it and sending it to be processed by the simulation.
    """

    def __init__(self):
        self.sensors = {} # sensor_id: (latitude, longitude)
        self.data = {} # sensor_id: {data}
        self.vehicles = {}

    def add_sensor(self, sensor_id, latitude, longitude):
        self.sensors[sensor_id] = (latitude, longitude)
        self.data[sensor_id] = []

    def add_vehicle(self, vehicle_id, vehicle_data):
        self.vehicles[vehicle_id] = vehicle_data

    def receive_data(self, data):
        """
        data_example: {
            "id": 22,
            "age": 39,
            "latitude": 40.62974973713478,
            "longitude": -8.65378593427814,
            "speed": 12.5,
            "acceleration": 0,
            "classification": 5,
            "detectionStationType": 15,
            "objectConfidence": 100,
            "sensorID": 1,
            "sensor": "radar",
            "test": null
        }
        """

        data = json.loads(data)
        vehicle_data = {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "speed": data["speed"],
            "acceleration": data["acceleration"],
            "classification": data["classification"]
        }
        self.add_vehicle(data["id"], vehicle_data)
        self.data[data["sensorID"]].append(data)