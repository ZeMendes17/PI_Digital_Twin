import React, {useState} from 'react';
import { Tooltip } from 'react-tooltip';
import './AddRandom.css';
import AddRandom_form from "../components/AddRandom_form";


const AddRandom = () => {

    const [quantity, setQuantity] = useState('');
    const [initialCoordinates, setInitialCoordinates] = useState('');
    const [finalCoordinates, setFinalCoordinates] = useState('');
    const [speed, setSpeed] = useState('');
    const [orientationAngle, setOrientationAngle] = useState('');

    const handleCancel = () => {
        window.location.href = '/';
    };

    const handleAdd = () => {
        window.location.href = '/';
    };

    return (
        <div className="random-page-container">
            <div className="random-page">

                <AddRandom_form/>

            </div>
        </div>
    );



};

export default AddRandom;
