import React, { useState, useEffect } from 'react';
import './TransportList.css';

/**
 * Componente TransportList
 * 
 * Muestra lista de unidades de transporte con filtrado y ordenamiento.
 * Permite seleccionar una unidad para ver detalles.
 */
function TransportList({ onSelectUnit, selectedUnitId }) {
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stateFilter, setStateFilter] = useState('');
  const [sortBy, setSortBy] = useState('eta');

  useEffect(() => {
    fetchUnits();
    // Actualizar lista cada 5 segundos
    const interval = setInterval(fetchUnits, 5000);
    return () => clearInterval(interval);
  }, [stateFilter, sortBy]);

  const fetchUnits = async () => {
    try {
      let url = '/api/transport-units';
      const params = new URLSearchParams();
      
      if (stateFilter) {
        params.append('state', stateFilter);
      }
      if (sortBy) {
        params.append('sort', sortBy);
      }
      
      if (params.toString()) {
        url += '?' + params.toString();
      }
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Error al obtener unidades');
      
      const data = await response.json();
      setUnits(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStateColor = (state) => {
    const colors = {
      'En_Ruta': '#4CAF50',
      'Detenido': '#FFC107',
      'Retraso': '#F44336',
      'Fuera_Servicio': '#9E9E9E'
    };
    return colors[state] || '#999';
  };

  const getStateIcon = (state) => {
    const icons = {
      'En_Ruta': '▶',
      'Detenido': '⏸',
      'Retraso': '⚠',
      'Fuera_Servicio': '✕'
    };
    return icons[state] || '?';
  };

  if (loading && units.length === 0) {
    return <div className="transport-list loading">Cargando unidades...</div>;
  }

  return (
    <div className="transport-list">
      <div className="list-header">
        <h2>Unidades de Transporte</h2>
        <div className="controls">
          <select 
            value={stateFilter} 
            onChange={(e) => setStateFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos los estados</option>
            <option value="En_Ruta">En Ruta</option>
            <option value="Detenido">Detenido</option>
            <option value="Retraso">Retraso</option>
            <option value="Fuera_Servicio">Fuera de Servicio</option>
          </select>
          
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="eta">Ordenar por ETA</option>
            <option value="state">Ordenar por Estado</option>
            <option value="name">Ordenar por Nombre</option>
            <option value="distance">Ordenar por Distancia</option>
          </select>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="units-container">
        {units.length === 0 ? (
          <div className="no-units">No hay unidades disponibles</div>
        ) : (
          units.map(unit => (
            <div
              key={unit.id}
              className={`unit-card ${selectedUnitId === unit.id ? 'selected' : ''}`}
              onClick={() => onSelectUnit(unit.id)}
            >
              <div className="unit-header">
                <div className="unit-name">{unit.name}</div>
                <div 
                  className="state-badge"
                  style={{ backgroundColor: getStateColor(unit.state) }}
                >
                  <span className="state-icon">{getStateIcon(unit.state)}</span>
                  <span className="state-text">{unit.state}</span>
                </div>
              </div>
              
              <div className="unit-info">
                <div className="info-row">
                  <span className="label">Ruta:</span>
                  <span className="value">{unit.route_id}</span>
                </div>
                <div className="info-row">
                  <span className="label">Progreso:</span>
                  <span className="value">{unit.current_location.route_progress.toFixed(1)}%</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${unit.current_location.route_progress}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default TransportList;
