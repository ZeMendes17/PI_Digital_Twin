from math import radians, sin, cos, sqrt, atan2, pi
import json

def calculate_distance(coord1, coord2):
    """
    Function to calculate the distance between two
    coordinates (latitude, longitude) in km.
    """
    # Approximate radius of the Earth in km
    R = 6373.0
    
    lat1 = radians(coord1[0])
    lon1 = radians(coord1[1])
    lat2 = radians(coord2[0])
    lon2 = radians(coord2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2

    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def calculate_bearing(coord1, coord2):
    """
    Function to calculate the bearing between two
    coordinates (latitude, longitude) in degrees.

    Note:   0deg is the North
            90deg is the East
            180deg is the South
            270deg is the West.

    Angle Type '0':
        0deg - 90deg and 270deg - 360deg => The vehicle is moving in the North of the radar
        90deg - 180deg and 180deg - 270deg => The vehicle is moving in the South of the radar
    
    Angle Type '1':
        0deg - 180deg => The vehicle is moving in the East of the radar
        180deg - 360deg => The vehicle is moving in the West of the radar
    """

    lat1 = radians(coord1[0])
    lon1 = radians(coord1[1])
    lat2 = radians(coord2[0])
    lon2 = radians(coord2[1])

    dlon = lon2 - lon1

    y = sin(dlon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

    return (atan2(y, x) * 180 / pi + 360) % 360

# TEST (REMOVE)

# get the data from the radar.json file
with open('radar.json', 'r') as file:
    radar_data = json.load(file)

# get the info for the first radar
radar = radar_data[0]
radar_coord = (radar['latitude'], radar['longitude'])

vehicle_coord = (40.63312662962101, -8.661403882757115)
vehicle_coord2 = (40.634726, -8.655101)

print(calculate_distance(radar_coord, vehicle_coord2))
print(calculate_bearing(radar_coord, vehicle_coord2))