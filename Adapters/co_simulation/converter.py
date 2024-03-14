import carla

import os
os.environ['PROJ_LIB'] = '/usr/share/proj'
os.environ['GDAL_DATA'] = '/us/share/gdal'


# Read the .osm data
f = open("ruadapega.osm", 'r')
osm_data = f.read()
f.close()

# Define the desired settings. In this case, default values.
settings = carla.Osm2OdrSettings()
settings.center_map = True


# Set OSM road types to export to OpenDRIVE
settings.set_osm_way_types(["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential"])
# Convert to .xodr
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# save opendrive file
f = open("afterconvert.xodr", 'w')
f.write(xodr_data)
f.close()