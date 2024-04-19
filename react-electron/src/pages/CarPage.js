import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './CarPage.css';
import {MapContainer} from "react-leaflet";
import MapComponent from "../components/MapComponent";

const CarPage = () => {
 const [quantity, setQuantity] = useState('');
 const [initialCoordinates, setInitialCoordinates] = useState('');
 const [finalCoordinates, setFinalCoordinates] = useState('');
 const [speed, setSpeed] = useState('');
 const [orientationAngle, setOrientationAngle] = useState('');

 return (
    <div className="car-page-container">
        <div className="car-page">
            <div>
                <p>instrução de como adicionar....</p>
            </div>
            <MapComponent/>

        </div>
    </div>
 );
};

export default CarPage;
