import React, { useState, useEffect } from 'react';
import Card from '../components/VehicleCard';
import { faRandom, faCar, faMotorcycle } from '@fortawesome/free-solid-svg-icons';
import './SimulationPage.css';
import Navbar from "../components/Navbar";
import AddRandom_form from "../components/AddRandom_form";
import socketIOClient from 'socket.io-client';

const SimulationPage = () => {
    const [message, setMessage] = useState('');

    useEffect(() => {
        const socket = socketIOClient('http://localhost:5000'); 

        socket.on('cars', (data) => {
            // Convertendo a mensagem ArrayBuffer para string
            const decoder = new TextDecoder();
            const decodedMessage = decoder.decode(data);
            
            setMessage(decodedMessage);
            console.log('Mensagem recebida do servidor:', decodedMessage);
        });

        return () => socket.disconnect();
    }, []);

    return (
        <div className="simulation-page-container">
            <div className="simulation-page">
                <p>WebSocket Message: {message}</p>
            </div>
        </div>
    );
};

export default SimulationPage;