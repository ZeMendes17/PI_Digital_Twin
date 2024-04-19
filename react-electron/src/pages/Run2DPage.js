import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Homepage.css';
import Navbar from "../components/Navbar";
import '../asset/teste.png'; // Importe a imagem de fundo
import Run2D_form from "../components/Run2D_form";


const Run2D = () => {

    const handleClick = () => {
        window.location.href = '/run2D';
    }

    return (
        <div>

            <div className="mt-7 container mx-auto px-4 py-8 flex items-center justify-center">

                <Run2D_form/>

            </div>


        </div>


    );
};

export default Run2D;
