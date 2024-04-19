import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './MapComponent.css';
import L from 'leaflet';
import {Tooltip} from "react-tooltip";
import axios from 'axios';

const initialMarkerIcon = new L.icon({
    iconUrl: 'https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const finalMarkerIcon = new L.icon({
    iconUrl: 'https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
});

const MapComponent = () => {
    const [clickCount, setClickCount] = useState(0);
    const [initialPosition, setInitialPosition] = useState(null);
    const [finalPosition, setFinalPosition] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false); // Estado para controlar se o modal está aberto

    const handleMapClick = (e) => {
        const { lat, lng } = e.latlng;
        console.log(`Latitude: ${lat}, Longitude: ${lng}`);

        if (clickCount === 0) {
            setInitialPosition({ lat, lng });
            setClickCount(1);
        } else {
            setFinalPosition({ lat, lng });
            setClickCount(0);
        }
    };

    const handleRemoveMarkers = () => {
        setInitialPosition(null);
        setFinalPosition(null);
        setClickCount(0);
    };

    const handleSubmit = () => {
        setIsModalOpen(true); // Abrir o modal ao clicar em "Submit"
        console.log('Initial position:', initialPosition);
        console.log('Final position:', finalPosition);
    }

    const closeModal = () => {
        setIsModalOpen(false); // Fechar o modal
    }

    const insertCar = () => {
        var car = {};
        if (initialPosition && finalPosition) {
            car = {
                "start": {
                    "lng": initialPosition.lng,
                    "lat": initialPosition.lat
                },
                "end": {
                    "lng": finalPosition.lng,
                    "lat": finalPosition.lat
                }
            };


            }

         else if (initialPosition) {
            car = {
                "start": {
                    "lng": initialPosition.lng,
                    "lat": initialPosition.lat
                }
            };


        }
         else {
            car = {
                "end": {
                    "lng": finalPosition.lng,
                    "lat": finalPosition.lat
                }
            };
        }

        axios.post('http://localhost:5000/api/addSimulatedCar', car)
                    .then(response => {
                        // Lida com a resposta da solicitação
                        console.log(response.data);
                    })
                    .catch(error => {
                        // Lida com erros na solicitação
                        console.error('Erro ao enviar objeto para a rota:', error);
                    });
    }

    return (
        <div>
            <MapContainer
                center={[40.63319824906938, -8.657974862473974]}
                zoom={16}
                className="map"
            >
                <TileLayer url="https://api.maptiler.com/maps/basic-v2/256/{z}/{x}/{y}.png?key=eKqBPyYHk8odwD7GfHAf" />
                {initialPosition && (
                    <Marker position={[initialPosition.lat, initialPosition.lng]} icon={initialMarkerIcon}>
                        <Popup>
                            Posição Inicial
                        </Popup>
                    </Marker>
                )}
                {finalPosition && (
                    <Marker position={[finalPosition.lat, finalPosition.lng]} icon={finalMarkerIcon}>
                        <Popup>
                            Posição Final
                        </Popup>
                    </Marker>
                )}

                <MapEventsHandler handleMapClick={handleMapClick} />
            </MapContainer>
            <div className="mt-5">
                <button className="mr-2 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                        onClick={handleRemoveMarkers}>Clear markers
                </button>
                <button
                    className="ml-2 bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                    data-tooltip-id="Firsttooltip"
                    data-tooltip-content="You need to select at least one initial position"
                    data-tooltip-place="bottom"
                    onClick={handleSubmit}
                    disabled={!initialPosition} // Desativa o botão se initialPosition for null
                >
                    Add car
                </button>
            </div>
            <Tooltip id="Firsttooltip"/>


            {isModalOpen && (
                <div className="modal">
                    <div className="modal-content text-gray-500">
                        <span className="close" onClick={closeModal}>&times;</span>
                        <h2 className="mb-5 ">You are adding a car with the following parameters:</h2>

                        <form className="mt-3">
                            <label htmlFor="Quantity">Quantity:</label>
                            <input type="number" id="Quantity" name="speed" min="1" max="100" required
                                   defaultValue={1}/>
                            <br/>
                            <label htmlFor="Departure">Departure (s):</label>
                            <input type="number" id="Departure" name="orientationAngle" min="0" max="3600" required
                                   defaultValue={0}/>
                            <br/>

                            <p>From: {JSON.stringify(initialPosition)}</p>

                            {finalPosition ? (
                                <p>To: {JSON.stringify(finalPosition)}</p>
                            ) : (
                                <p>To: Random position</p>

                            )}


                        </form>
                        <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                                onClick={insertCar}>Submit
                        </button>


                    </div>
                </div>
            )}
        </div>
    );
};

const MapEventsHandler = ({handleMapClick}) => {
    useMapEvents({
        click: (e) => handleMapClick(e),
    });
    return null;
};

export default MapComponent;
