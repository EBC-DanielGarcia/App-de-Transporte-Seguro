"""
Sistema Universitario de Monitoreo de Transporte en Tiempo Real.

Aplicación principal que inicia el servidor Flask y configura las rutas API.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
from models.transport_unit import TransportUnit
from models.location import Location
from models.route import Route
from models.stop import Stop
from models.transport_state import TransportState
from services.simulation_engine import SimulationEngine
from services.simulation_scheduler import SimulationScheduler
from services.eta_calculator import ETACalculator
from services.delay_detection_engine import DelayDetectionEngine
from services.persistence_service import PersistenceService
from services.realtime_update_service import RealtimeUpdateService
from services.history_service import HistoryService
from services.route_service import RouteService
from services.dashboard_service import DashboardService, SortBy
from seed_data import seed_database

# Crear aplicación Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuración
app.config['DEBUG'] = os.getenv('FLASK_ENV', 'development') == 'development'
app.config['JSON_SORT_KEYS'] = False

# Inicializar servicios
persistence_service = PersistenceService()
eta_calculator = ETACalculator()
delay_detection_engine = DelayDetectionEngine(eta_calculator, persistence_service)
realtime_update_service = RealtimeUpdateService()
history_service = HistoryService(persistence_service)
route_service = RouteService()
dashboard_service = DashboardService(route_service, eta_calculator, history_service)
simulation_engine = SimulationEngine()
simulation_scheduler = SimulationScheduler(simulation_engine)

# Almacenamiento global de unidades de transporte
transport_units = {}

# Cargar datos de ejemplo
routes, units = seed_database(app, route_service, dashboard_service)
for unit in units:
    transport_units[unit.id] = unit


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de salud."""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Sistema de Monitoreo de Transporte en Tiempo Real'
    }, 200


@app.route('/api/info', methods=['GET'])
def info():
    """Endpoint de información de la aplicación."""
    return {
        'name': 'Sistema Universitario de Monitoreo de Transporte en Tiempo Real',
        'version': '1.0.0',
        'description': 'Prototipo académico para visualizar ubicación, estado y tiempos estimados de transporte',
        'timestamp': datetime.now().isoformat()
    }, 200


# ============================================================================
# Endpoints para Unidades de Transporte
# ============================================================================

@app.route('/api/transport-units', methods=['GET'])
def get_transport_units():
    """
    Obtener lista de todas las unidades de transporte.
    
    Query parameters:
    - state: Filtrar por estado (En_Ruta, Detenido, Retraso, Fuera_Servicio)
    - sort: Ordenar por (eta, state, name, distance)
    """
    units = dashboard_service.get_all_transport_units()
    
    # Filtrar por estado si se especifica
    state_filter = request.args.get('state')
    if state_filter:
        try:
            state = TransportState(state_filter)
            units = dashboard_service.filter_by_state(state)
        except ValueError:
            return {'error': f'Estado inválido: {state_filter}'}, 400
    
    # Ordenar si se especifica
    sort_by = request.args.get('sort', 'eta')
    try:
        sort_enum = SortBy(sort_by)
        units = dashboard_service.sort_units(units, sort_enum)
    except ValueError:
        return {'error': f'Criterio de ordenamiento inválido: {sort_by}'}, 400
    
    return jsonify([
        {
            'id': unit.id,
            'name': unit.name,
            'route_id': unit.route_id,
            'state': unit.state.value,
            'current_location': {
                'latitude': unit.current_location.latitude,
                'longitude': unit.current_location.longitude,
                'route_progress': unit.current_location.route_progress
            },
            'speed': unit.speed
        }
        for unit in units
    ]), 200


@app.route('/api/transport-units/<unit_id>', methods=['GET'])
def get_transport_unit(unit_id):
    """Obtener detalles completos de una unidad de transporte."""
    details = dashboard_service.get_unit_details(unit_id)
    
    if details is None:
        return {'error': f'Unidad no encontrada: {unit_id}'}, 404
    
    return jsonify(details), 200


@app.route('/api/transport-units/<unit_id>/history', methods=['GET'])
def get_transport_unit_history(unit_id):
    """Obtener historial de eventos de una unidad de transporte."""
    unit = dashboard_service.get_transport_unit(unit_id)
    if unit is None:
        return {'error': f'Unidad no encontrada: {unit_id}'}, 404
    
    history = history_service.get_history(unit_id)
    
    return jsonify({
        'transport_unit_id': unit_id,
        'events': [
            {
                'id': event.id,
                'type': event.type,
                'timestamp': event.timestamp.isoformat(),
                'data': event.data
            }
            for event in history
        ],
        'summary': history_service.get_summary(unit_id)
    }), 200


# ============================================================================
# Endpoints para Rutas
# ============================================================================

@app.route('/api/routes', methods=['GET'])
def get_routes():
    """Obtener lista de todas las rutas disponibles."""
    routes = route_service.get_all_routes()
    
    return jsonify([
        {
            'id': route.id,
            'name': route.name,
            'total_distance': route.total_distance,
            'estimated_duration': route.estimated_duration,
            'stops_count': len(route.stops)
        }
        for route in routes
    ]), 200


@app.route('/api/routes/<route_id>', methods=['GET'])
def get_route(route_id):
    """Obtener detalles completos de una ruta."""
    route_info = route_service.get_route_info(route_id)
    
    if route_info is None:
        return {'error': f'Ruta no encontrada: {route_id}'}, 404
    
    return jsonify(route_info), 200


@app.route('/api/routes/<route_id>/stops', methods=['GET'])
def get_route_stops(route_id):
    """Obtener paradas de una ruta."""
    stops = route_service.get_stops_for_route(route_id)
    
    if stops is None:
        return {'error': f'Ruta no encontrada: {route_id}'}, 404
    
    return jsonify([
        {
            'id': stop.id,
            'name': stop.name,
            'latitude': stop.latitude,
            'longitude': stop.longitude,
            'distance_from_start': stop.distance_from_start,
            'estimated_stop_duration': stop.estimated_stop_duration
        }
        for stop in stops
    ]), 200


# ============================================================================
# Endpoints para Simulación
# ============================================================================

@app.route('/api/simulations/start', methods=['POST'])
def start_simulation():
    """
    Iniciar simulación para una unidad de transporte.
    
    Body JSON:
    {
        "transport_unit_id": "unit-1",
        "route_id": "route-1"
    }
    """
    data = request.get_json()
    
    if not data or 'transport_unit_id' not in data or 'route_id' not in data:
        return {'error': 'Faltan parámetros: transport_unit_id, route_id'}, 400
    
    unit_id = data['transport_unit_id']
    route_id = data['route_id']
    
    # Verificar que la ruta existe
    route = route_service.get_route(route_id)
    if route is None:
        return {'error': f'Ruta no encontrada: {route_id}'}, 404
    
    # Crear o actualizar unidad de transporte
    if unit_id not in transport_units:
        unit = TransportUnit(
            id=unit_id,
            name=data.get('name', f'Unidad {unit_id}'),
            route_id=route_id,
            current_location=Location(
                latitude=route.stops[0].latitude,
                longitude=route.stops[0].longitude,
                route_progress=0,
                timestamp=datetime.now()
            ),
            state=TransportState.EN_RUTA,
            speed=data.get('speed', 40)
        )
        transport_units[unit_id] = unit
        dashboard_service.add_transport_unit(unit)
    else:
        unit = transport_units[unit_id]
    
    # Iniciar simulación
    simulation_scheduler.add_transport_unit(unit, route)
    
    if not simulation_scheduler.is_scheduler_running():
        simulation_scheduler.start_scheduler()
    
    return jsonify({
        'message': 'Simulación iniciada',
        'transport_unit_id': unit_id,
        'route_id': route_id
    }), 200


@app.route('/api/simulations/stop', methods=['POST'])
def stop_simulation():
    """
    Detener simulación para una unidad de transporte.
    
    Body JSON:
    {
        "transport_unit_id": "unit-1"
    }
    """
    data = request.get_json()
    
    if not data or 'transport_unit_id' not in data:
        return {'error': 'Falta parámetro: transport_unit_id'}, 400
    
    unit_id = data['transport_unit_id']
    
    # Detener simulación
    simulation_scheduler.remove_transport_unit(unit_id)
    
    return jsonify({
        'message': 'Simulación detenida',
        'transport_unit_id': unit_id
    }), 200


# ============================================================================
# Endpoints para Dashboard
# ============================================================================

@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Obtener resumen del dashboard con estadísticas generales."""
    summary = dashboard_service.get_dashboard_summary()
    return jsonify(summary), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
