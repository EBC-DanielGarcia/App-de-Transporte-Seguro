import React, { useState, useEffect } from 'react';
import './RouteVisualization.css';

/**
 * Componente RouteVisualization
 * 
 * Visualiza el recorrido de una unidad de transporte con todas las paradas
 * y la posición actual.
 */
function RouteVisualization({ unitId, routeId }) {
  const [route, setRoute] = useState(null);
  const [unitDetails, setUnitDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!routeId || !unitId) {
      setRoute(null);
      setUnitDetails(null);
      setLoading(false);
      return;
    }

    fetchData();
    // Actualizar cada 3 segundos
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [routeId, unitId]);

  const fetchData = async () => {
    try {
      const [routeRes, unitRes] = await Promise.all([
        fetch(`/api/routes/${routeId}`),
        fetch(`/api/transport-units/${unitId}`)
      ]);

      if (!routeRes.ok || !unitRes.ok) {
        throw new Error('Error al obtener datos');
      }

      const routeData = await routeRes.json();
      const unitData = await unitRes.json();

      setRoute(routeData);
      setUnitDetails(unitData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!routeId || !unitId) {
    return (
      <div className="route-visualization empty">
        <p>Selecciona una unidad para ver el recorrido</p>
      </div>
    );
  }

  if (loading && !route) {
    return <div className="route-visualization loading">Cargando recorrido...</div>;
  }

  if (error) {
    return <div className="route-visualization error">Error: {error}</div>;
  }

  if (!route || !unitDetails) {
    return <div className="route-visualization empty">No hay datos disponibles</div>;
  }

  const progress = unitDetails.current_location.route_progress;
  const currentStop = unitDetails.current_stop;
  const nextStop = unitDetails.next_stop;

  return (
    <div className="route-visualization">
      <div className="route-header">
        <h3>{route.name}</h3>
        <div className="route-info">
          <span>{route.total_distance.toFixed(1)} km</span>
          <span>•</span>
          <span>{route.stops_count} paradas</span>
        </div>
      </div>

      <div className="route-container">
        {/* Línea de progreso */}
        <div className="progress-line-container">
          <div className="progress-line">
            <div 
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div 
            className="progress-indicator"
            style={{ left: `${progress}%` }}
          >
            <div className="indicator-dot"></div>
          </div>
        </div>

        {/* Paradas */}
        <div className="stops-container">
          {route.stops.map((stop, index) => {
            const stopProgress = (stop.distance_from_start / route.total_distance) * 100;
            const isCurrentStop = currentStop && currentStop.id === stop.id;
            const isNextStop = nextStop && nextStop.id === stop.id;
            const isPassed = progress > stopProgress;

            return (
              <div
                key={stop.id}
                className={`stop-marker ${isCurrentStop ? 'current' : ''} ${isNextStop ? 'next' : ''} ${isPassed ? 'passed' : ''}`}
                style={{ left: `${stopProgress}%` }}
                title={stop.name}
              >
                <div className="stop-dot"></div>
                <div className="stop-label">
                  <div className="stop-name">{stop.name}</div>
                  <div className="stop-distance">{stop.distance_from_start.toFixed(1)} km</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Información de paradas */}
      <div className="stops-info">
        <div className="info-section">
          <h4>Parada Actual</h4>
          {currentStop ? (
            <div className="stop-details">
              <div className="detail-row">
                <span className="label">Nombre:</span>
                <span className="value">{currentStop.name}</span>
              </div>
              <div className="detail-row">
                <span className="label">Distancia:</span>
                <span className="value">{currentStop.distance_from_start.toFixed(1)} km</span>
              </div>
            </div>
          ) : (
            <div className="no-data">No hay parada actual</div>
          )}
        </div>

        <div className="info-section">
          <h4>Próxima Parada</h4>
          {nextStop ? (
            <div className="stop-details">
              <div className="detail-row">
                <span className="label">Nombre:</span>
                <span className="value">{nextStop.name}</span>
              </div>
              <div className="detail-row">
                <span className="label">Distancia:</span>
                <span className="value">{nextStop.distance_from_start.toFixed(1)} km</span>
              </div>
              <div className="detail-row">
                <span className="label">ETA:</span>
                <span className="value eta">{nextStop.eta.toFixed(0)} min</span>
              </div>
            </div>
          ) : (
            <div className="no-data">Destino final alcanzado</div>
          )}
        </div>

        <div className="info-section">
          <h4>Progreso General</h4>
          <div className="progress-info">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="progress-text">{progress.toFixed(1)}% completado</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RouteVisualization;
