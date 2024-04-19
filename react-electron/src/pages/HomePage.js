import React from 'react';
import { Tooltip } from 'react-tooltip';
import './Homepage.css';


const HomePage = () => {



    const handleClick = () => {
        window.location.href = '/run2D';
    }

    const handleClick3D = () => {
        window.location.href = '/run3D';
    }

    return (
        <div>

            <div className="container mx-auto pt-20 mt-20">
                <div className="text-center mb-20">
                    <h1>Aveiro Digital Twin</h1>
                    <h2>The objective of this project is to develop a platform that supports the concept of Digital Twin with city information. The platform should allow the visualization of data from the physical twin as well as the creation of simulated scenarios that blend with real events. </h2>
                </div>

                <h3 className="text-center text-xl font-bold mb-8">Run Simulation</h3>

                <div className="flex justify-center">
                    <button
                        data-tooltip-id="Firsttooltip"
                        data-tooltip-content="Make sure you have SUMO installed"
                        data-tooltip-place="bottom"
                        className="mr-5 bg-green-500 hover:bg-green-700 text-white font-bold py-6 px-12 mr-4 rounded text-xl"
                        onClick={handleClick}
                    >
                        2D
                    </button>
                    <button
                        data-tooltip-id="Secondtooltip"
                        data-tooltip-content="Make sure you have SUMO and CARLA installed"
                        data-tooltip-place="bottom"
                        className="ml-5 bg-green-500 hover:bg-green-700 text-white font-bold py-6 px-12 rounded text-xl"
                        data-tip="Outro texto do Tooltip para 3D"
                        data-for="botao3DTooltip" // Referência ao tooltip correspondente
                        onClick={handleClick3D}
                    >
                        3D
                    </button>
                </div>
            </div>
            <Tooltip id="Firsttooltip"/>
            <Tooltip id="Secondtooltip"/>
        </div>
    );
};

export default HomePage;
