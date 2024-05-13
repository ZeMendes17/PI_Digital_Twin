# SUMO installation

## Installation

### Requirements

- Docker
- Git

### Installation

In order to install SUMO, run the following command:

```bash
./install_sumo.sh
```

Do not forget to give execution permission to the script:

```bash
chmod +x install_sumo.sh
```

## Usage

If you want to run SUMO, you can use the following command:

```bash
docker run -it --rm\
    --env="DISPLAY" \
    --volume="/etc/group:/etc/group:ro" \
    --volume="/etc/passwd:/etc/passwd:ro" \
    --volume="/etc/shadow:/etc/shadow:ro" \
    --volume="/etc/sudoers.d:/etc/sudoers.d:ro" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --user=$USER \
    docker-sumo \
    bash
```

In our case, we do not need to run SUMO rigth now, thus this command is not included in the script.
We will use this command only in the main Docker Compose file.