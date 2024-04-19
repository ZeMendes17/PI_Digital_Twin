import React from 'react';
import axios from 'axios';
import teste from '../asset/carla.jpg';

const Run3D_form = () => {

    const API = "http://localhost:5000/api";

    const handleSubmit = async (event) => {

        event.preventDefault();  

        try {
            const response = await axios.post(`${API}/run3D`);
            if (response.status === 200) {
                console.log('Simulação 3D iniciada com sucesso:', response.data);
                window.location.href = '/simulation';
            }
        } catch (error) {
            console.error('Erro ao iniciar a simulação 3D:', error);
        }
    };

    return (
        <div
            className="bg-cover bg-center bg-no-repeat"
            style={{
                backgroundImage: `url(${teste})`,
                height: '100vh',
                width: '100vw', // Ajuste a largura da imagem de fundo para cobrir toda a largura da tela
            }}
        >
            <div className="container mx-auto px-4 py-8 flex items-center justify-center">
                <div className="w-full max-w-lg bg-white bg-opacity-90 rounded-lg shadow-lg p-8">
                    <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label htmlFor="configFile" className="block text-gray-700 text-sm font-bold mb-2">
                                Configuration File (.xml)
                            </label>
                            <input
                                type="file"
                                id="configFile"
                                name="configFile"
                                accept=".xml"
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            />
                        </div>
                        <div
                            className="mb-4 flex items-center"> {/* Adicionado flex e items-center para alinhar o checkbox à esquerda */}
                            <div
                                className="inline-flex items-center"> {/* Adicionado para envolver o checkbox e o texto */}
                                <input
                                    type="checkbox"
                                    id="addRealData"
                                    name="addRealData"
                                    className="form-checkbox text-blue-500 h-5 w-5"
                                />
                                <span className="ml-2 text-sm">Add real data?</span>
                            </div>
                        </div>
                        <div className="mb-4">
                            <p className="text-sm text-gray-600">
                                The 3D simulation will be performed using CARLA. Make sure your system meets the
                                following minimum requirements: Quad-core CPU, 8 GB RAM, NVIDIA GTX 1060. For best
                                performance, an NVIDIA RTX 2070 or higher GPU and 16 GB RAM are recommended.
                            </p>
                        </div>
                        <div className="text-center">
                            <button type="submit"
                                    className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                                Start Simulation
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Run3D_form;