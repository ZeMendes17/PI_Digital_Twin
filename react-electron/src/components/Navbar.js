// src/components/Navbar.js

import React from 'react';
import './Navbar.css'; // Vamos criar este arquivo CSS para os estilos

function Navbar() {
 return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="navbar-logo">
          <h1>Digital Twin</h1>
        </div>
        <div className="navbar-links">
          <a href="#">User</a>
          <a href="#">Settings</a>
        </div>
      </div>
    </nav>
 );
}

export default Navbar;
