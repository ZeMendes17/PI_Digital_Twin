import React, {useState} from 'react';
import teste from '../asset/teste.png';
import axios from "axios";
import {Tooltip} from "react-tooltip";
import {renderToString} from "react-dom/server"; // Importe a imagem de fundo




const Run2D_form = () => {

    const API = "http://localhost:5000/api";
    const [carQuantity, setCarQuantity] = useState(""); // Estado para armazenar a quantidade de carros

    const handleSubmit = async (event) => {
        event.preventDefault();

        try {
            const response = await axios.post(`${API}/addRandomTraffic?qtd=${carQuantity}`);
            if (response.status === 200) {
                console.log('Solicitação enviada com sucesso:', response.data);
                window.location.href = '/simulation';
            }
        } catch (error) {
            console.error('Erro ao enviar a solicitação:', error);
        }
    };

    const generateTooltipContent = () => {
        const tooltipContent = <p>Tip: Low traffic - 100 cars; Medium traffic - 500 cars; High traffic - 1000 cars</p>;
        const tooltipHtml = renderToString(tooltipContent);
        const strippedHtml = new DOMParser().parseFromString(tooltipHtml, 'text/html').body.innerText;
        return strippedHtml;
    };

    return (

            <div className="container mx-auto px-4 py-8 flex items-center justify-center">
                <div className="w-full max-w-lg bg-white bg-opacity-90 rounded-lg shadow-lg p-8">
                    <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label htmlFor="configFile" className="text-gray-500 block mb-1">How many cars do you want to add?</label>
                            <input
                                type="number"
                                id="quantity"
                                className="w-full px-4 py-2 border rounded-md text-gray-700 focus:outline-none focus:border-green-500"
                                onChange={(e) => setCarQuantity(e.target.value)}
                                data-tooltip-id="Firsttooltip"
                                data-tooltip-content={generateTooltipContent()}
                                data-tooltip-place="bottom"
                            />
                            <Tooltip id="Firsttooltip"/>
                        </div>

                        <div className="mb-4">
                            <p className="text-sm text-gray-500">You are adding vehicles dynamically and randomly, meaning they will have random types, routes, and behaviors.</p>
                            <p className="text-sm text-gray-500">You can see the vehicles in the SUMO interface.</p>

                        </div>
                        <div className="text-center">
                            <button type="submit"
                                    className="px-6 py-3 bg-green-500 text-white font-bold rounded-md hover:bg-green-600">Add random traffic
                            </button>
                        </div>
                    </form>
                </div>


        </div>
    );
};

export default Run2D_form;
