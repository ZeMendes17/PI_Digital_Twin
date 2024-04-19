import React from 'react';
import Run3D_form from '../components/Run3D_form';  
import './Homepage.css';
import Navbar from "../components/Navbar";
import '../asset/teste3d.png'; 

const Run3DPage = () => {

    const handleClick = () => {
        window.location.href = '/run3D';
    }

    return (
        <div>

            <div className="mt-7 container mx-auto px-4 py-8 flex items-center justify-center">

                <Run3D_form/>

            </div>

        </div>
    );
};

export default Run3DPage;