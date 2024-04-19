#!/bin/bash

# Function to clean up and exit
cleanup() {
    echo "Exiting..."
    # Kill the Carla process
    pkill -f CarlaUE4.sh
    # Kill the PythonAPI process
    pkill -f config.py
    exit 1
}

# Trap Ctrl+C and call the cleanup function
trap cleanup SIGINT

echo "Starting Carla..."
bash ~/Desktop/CARLA_0.9.15/CarlaUE4.sh -windowed -ResX=800 -ResY=600 &
sleep 5
echo "Carla is running"
echo "Loading Map..."
python3 ~/Desktop/CARLA_0.9.15/PythonAPI/util/config.py -x ~/Desktop/PI_Digital_Twin/Adapters/co_simulation/sumo_configuration/simple-map/aveiro.xodr &

# Wait for Ctrl+C
wait