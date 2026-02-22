import React, { useState, useEffect } from 'react';
import './TransportDetails.css';

/**
 * Componente TransportDetails
 * 
 * Muestra detalles completos de una unidad de transporte seleccionada,
 * incluyendo ubicación, estado, ETA y historial.
 */
function TransportDetails({ unitId }) {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (!unitId) {
      setDetails(null);
      setLoading(false);
      return;
    }

    fetchDetails();
    // Actualizar detalles cada 3 segundos
    const interval = setInterval(fetchDetails, 3000);
    return () => clearInterval(interval);
  }, [unitId]);

  const fetchDetails = async () => {
    try {
      const response = await fetch(`/api/transport-units/${unitId}`);
      if (!response.ok) throw new Error('Error al obtener detalles');
      
      const data = await response.json();
      setDetails(data);
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

  if (!unitId) {
    return (
      <div className="transport-details empty">
        <div className="empty-state">
          <p>Selecciona una unidad para ver detalles</p>
        </div>
      </div>
    );
  }

  if (loading && !details) {
    return <div className="transport-details loading">Cargando detalles...</div>;
  }

  if (error) {
    return <div className="transport-details error">Error: {error}</div>;
  }

  if (!details) {
    return <div className="transport-details empty">No hay datos disponibles</div>;
  }

  return (
    <div className="transport-details">
      <div className="details-header">
        <div className="header-title">
          <h2>{details.name}</h2>
          <p className="route-name">{details.route_name}</p>
        </div>
        <div 
          className="state-badge-large"
          style={{ backgroundColor: getStateColor(details.state) }}
        >
          <span className="state-icon">{getStateIcon(details.state)}</span>
          <span className="state-text">{details.state}</span>
        </div>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Resumen
        </button>
        <button 
          className={`tab ${activeTab === 'route' ? 'active' : ''}`}
          onClick={() => setActiveTab('route')}
        >
          Recorrido
        </button>
        <button 
          className={`tab ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Métricas
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="section">
              <h3>Ubicación Actual</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="label">Latitud:</span>
                  <span className="value">{details.current_location.latitude.toFixed(4)}</span>
                </div>
                <div className="info-item">
                  <span className="label">Longitud:</span>
                  <span className="value">{details.current_location.longitude.toFixed(4)}</span>
                </div>
                <div className="info-item">
                  <span className="label">Progreso:</span>
                  <span className="value">{details.current_location.route_progress.toFixed(1)}%</span>
                </div>
                <div className="info-item">
                  <span className="label">Velocidad:</span>
                  <span className="value">{details.speed} km/h</span>
                </div>
              </div>
            </div>

            <div className="section">
              <h3>Parada Actual</h3>
              {details.current_stop ? (
                <div className="stop-info">
                  <div className="stop-name">{details.current_stop.name}</div>
                  <div className="stop-detail">
                    Distancia desde inicio: {details.current_stop.distance_from_start.toFixed(1)} km
                  </div>
                </div>
              ) : (
                <div className="no-data">No hay parada actual</div>
              )}
            </div>

            <div className="section">
              <h3>Próxima Parada</h3>
              {details.next_stop ? (
                <div className="stop-info">
                  <div className="stop-name">{details.next_stop.name}</div>
                  <div className="stop-detail">
                    Distancia: {details.next_stop.distance_from_start.toFixed(1)} km
                  </div>
                  <div className="eta-badge">
                    ETA: {details.next_stop.eta.toFixed(0)} min
                  </div>
                </div>
              ) : (
                <div className="no-data">Destino final alcanzado</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'route' && (
          <div className="route-tab">
            <div className="section">
              <h3>Tiempos Estimados de Llegada</h3>
              <div className="etas-list">
                {Object.entries(details.etas).map(([stopId, eta]) => (
                  <div key={stopId} className="eta-item">
                    <span className="stop-id">{stopId}</span>
                    <span className="eta-value">{eta.toFixed(0)} min</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="metrics-tab">
            <div className="section">
              <h3>Métricas de Desempeño</h3>
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-label">Tiempo Total</div>
                  <div className="metric-value">{details.metrics.total_travel_time} min</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Retrasos Acumulados</div>
                  <div className="metric-value">{details.metrics.total_delay_time} min</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Cantidad de Retrasos</div>
                  <div className="metric-value">{details.metrics.delay_count}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Retraso Promedio</div>
                  <div className="metric-value">{details.metrics.average_delay.toFixed(1)} min</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Puntualidad</div>
                  <div className="metric-value">{details.metrics.on_time_percentage.toFixed(1)}%</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default TransportDetails;
