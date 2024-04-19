# PI_Digital_Twin
Project for the Project in Informatics class

## Team

| Name           | **Email**            | NMEC   
| -------------  | -------------------- | ----- 
| Bernardo Pinto | bernardopinto@ua.pt  | 105926
| Filipe Obrist  | filipe.obrist@ua.pt  | 107471 
| Mariana Perna  | marianaperna@ua.pt   | 108067
| José Mendes    | mendes.j@ua.pt       | 107188
| Rafaela Dias   | rafaelasdias@ua.pt   | 108782

## How to run

- Install requirements
```bash
pip install -r requirements.txt
```

- Run carla server and load map
```bash
./runCarla.sh
```


- Run carla server
```bash
./CarlaUE4.sh
```

- Load map
```bash
python3 config.py -x ~/Desktop/PI_Digital_Twin/Adapters/co_simulation/sumo_configuration/simple-map/map-clean.xodr
```

- Run co-simulation
```bash
 python3 simulation_3D.py sumo_configuration/ruadapega.sumocfg --tls-manager carla --sumo-gui
```


## Export map

- Geramos o .osm

- Limpamos no JOSM

- Apagamos as linhas de delete 

```
osmfilter in.osm --drop-tags="@action='delete'" -o=out.osm
```

- com Adapters/co_simulation/map_adjustor/osm_to_xodr/main.py
    - Crio um header ideal para o xodr
    - Crio um novo arquivo .osm modificado (map_modified_for_Carla.osm)
    
- com Adapters/co_simulation/map_adjustor/osm_to_xodr/converter.py crio o xodr para o carla (map_modified_for_Carla.osmcomo parametro dentro do .py ) ***

- A partir do xodr é que vou criar a network para ser interpretada pelo sumo
```
python3 Adapters/co_simulation/map_adjustor/xodr_to_netxml/netconvert_carla.py --output *out*.net.xml --guess-tls ~/Desktop/PI_Digital_Twin/Adapters/co_simulation/sumo_configuration/simple-map/*in*.xodr 
```

- Altero o .sumocfg com as entradas desejadas




