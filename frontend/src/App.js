import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TransportList from './components/TransportList';
import TransportDetails from './components/TransportDetails';
import RouteVisualization from './components/RouteVisualization';
import './App.css';

function App() {
  const [appInfo, setAppInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedUnitId, setSelectedUnitId] = useState(null);
  const [selectedUnitRouteId, setSelectedUnitRouteId] = useState(null);

  useEffect(() => {
    // Obtener información de la aplicación
    fetch('/api/info')
      .then(response => response.json())
      .then(data => {
        setAppInfo(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const handleSelectUnit = (unitId) => {
    setSelectedUnitId(unitId);
    // Obtener route_id de la unidad
    fetch(`/api/transport-units/${unitId}`)
      .then(response => response.json())
      .then(data => {
        setSelectedUnitRouteId(data.route_id);
      })
      .catch(err => console.error('Error:', err));
  };

  if (loading) {
    return <div className="container"><p>Cargando...</p></div>;
  }

  if (error) {
    return <div className="container error"><p>Error: {error}</p></div>;
  }

  return (
    <Router>
      <div className="App">
        <header className="header">
          <h1>{appInfo?.name || 'Sistema de Monitoreo de Transporte'}</h1>
          <p className="subtitle">{appInfo?.description}</p>
        </header>
        
        <main className="main-content">
          <Routes>
            <Route 
              path="/" 
              element={
                <Dashboard 
                  selectedUnitId={selectedUnitId}
                  selectedUnitRouteId={selectedUnitRouteId}
                  onSelectUnit={handleSelectUnit}
                />
              } 
            />
          </Routes>
        </main>

        <footer className="footer">
          <p>Versión {appInfo?.version} - Sistema Académico</p>
        </footer>
      </div>
    </Router>
  );
}

function Dashboard({ selectedUnitId, selectedUnitRouteId, onSelectUnit }) {
  return (
    <div className="dashboard">
      <div className="dashboard-layout">
        <TransportList 
          onSelectUnit={onSelectUnit}
          selectedUnitId={selectedUnitId}
        />
        
        <div className="dashboard-right">
          <TransportDetails unitId={selectedUnitId} />
          
          {selectedUnitId && selectedUnitRouteId && (
            <RouteVisualization 
              unitId={selectedUnitId}
              routeId={selectedUnitRouteId}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
