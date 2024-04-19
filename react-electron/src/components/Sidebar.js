// src/components/Sidebar.js

import React from 'react';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faRandom, faRobot, faCar, faMotorcycle, faBicycle, faPersonWalking } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { Link } from 'react-router-dom';
import './Sidebar.css';
import { Tooltip } from 'react-tooltip';


library.add(faRandom, faRobot, faCar, faMotorcycle, faBicycle, faPersonWalking);
function Sidebar() {
 return (
    <div className="sidebar">
      <div className="sidebar-content">

        <div className="sidebar-cards">
          <Link to="/addRandom" data-tooltip-id="Firsttooltip"
                data-tooltip-content="Add vehicles with random directions"
                data-tooltip-place="bottom">
          <div className="card">
            <div className="card-icon">
              <FontAwesomeIcon icon="random" size="2x" />
            </div>
            <h2>Random</h2>
          </div>
          </Link>
          <Link to="/car">
            <div className="card">
              <div className="card-icon">
                <FontAwesomeIcon icon={faCar} size="2x" />
              </div>
              <h2>Car</h2>
            </div>
          </Link>
          <div className="card">
            <div className="card-icon">
              <FontAwesomeIcon icon="motorcycle" size="2x" />
            </div>
            <h2>Motorcycle</h2>
          </div>
          <div className="card">
            <div className="card-icon">
              <FontAwesomeIcon icon="bicycle" size="2x" />
            </div>
            <h2>Bicycle</h2>
          </div>
          <div className="card">
            <div className="card-icon">
              <FontAwesomeIcon icon="person-walking" size="2x" />
            </div>
            <h2>Pedestrian</h2>
          </div>
          <div className="card">
            <div className="card-icon">
              <FontAwesomeIcon icon="robot" size="2x" />
            </div>
            <h2>Autonomous Vehicle</h2>
          </div>
        </div>
      </div>
      <Tooltip id="Firsttooltip"/>

    </div>
 );
}

export default Sidebar;
