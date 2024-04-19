import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import Navbar from './components/Navbar'; 
import Sidebar from './components/Sidebar';
import SimulationPage from './pages/SimulationPage'; 
import CarPage from './pages/CarPage'; 
import './App.css';
import axios from 'axios';
import HomePage from "./pages/HomePage";
import Run2D from "./pages/Run2DPage";
import AddRandom from "./pages/AddRandom";
import Run3DPage from './pages/Run3DPage';

const api = "http://localhost:5000/api";

function App() {


  function runPythonScript() {
    axios.post(`${api}/run`)
      .then(response => {
        console.log('Comando executado com sucesso:', response.data);
        // Faça algo com os dados retornados, se necessário
      })
      .catch(error => {
        console.error('Erro ao executar o comando:', error);
      });
  }

  return (
    <Router>
      <div className="App">
<Navbar />
        <Routes>
          <Route path="/" element={<HomePage /> } />
          <Route path="/run2D" element={ <Run2D />} />
          <Route path="/run3D" element={<Run3DPage />} />
          <Route path="/car" element={<><Sidebar /> <CarPage /></>} />
          <Route path="/button" element={<><Sidebar /> <button onClick={runPythonScript}>RUN</button></>} />
          <Route path="/simulation" element={<><Sidebar /> <SimulationPage /></>} />
          <Route path="/addRandom" element={<><Sidebar /> <AddRandom /></>} />
        </Routes>
      </div>
    </Router>
 );
}

export default App;
