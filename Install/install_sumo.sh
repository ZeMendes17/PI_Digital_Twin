#!/bin/bash

# Clone the repository
git clone git@github.com:bogaotory/docker-sumo.git
cd docker-sumo

# Change your_username (line 8 of Dockerfile) to your username (i.e. the output of echo "$USER")
sed -i "s/your_username/$(echo "$USER")/g" Dockerfile

# # Build the docker image
# docker build - < Dockerfile -t docker-sumo

# # Remove the repository
# cd ..
# rm -rf docker-sumo