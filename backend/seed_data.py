"""
Script de seed para cargar datos de ejemplo en la aplicación.

Crea rutas, paradas y unidades de transporte de ejemplo para demostración.
"""

from datetime import datetime
from models.route import Route
from models.stop import Stop
from models.transport_unit import TransportUnit
from models.location import Location
from models.transport_state import TransportState


def create_sample_routes():
    """Crear rutas de ejemplo."""
    
    # Ruta 1: Centro - Periferia
    route1_stops = [
        Stop(
            id="stop-1-1",
            name="Centro Histórico",
            latitude=19.4326,
            longitude=-99.1332,
            distance_from_start=0,
            estimated_stop_duration=2
        ),
        Stop(
            id="stop-1-2",
            name="Estación Central",
            latitude=19.4330,
            longitude=-99.1300,
            distance_from_start=3.5,
            estimated_stop_duration=3
        ),
        Stop(
            id="stop-1-3",
            name="Parque Metropolitano",
            latitude=19.4350,
            longitude=-99.1250,
            distance_from_start=7.2,
            estimated_stop_duration=2
        ),
        Stop(
            id="stop-1-4",
            name="Hospital General",
            latitude=19.4380,
            longitude=-99.1180,
            distance_from_start=11.5,
            estimated_stop_duration=3
        ),
        Stop(
            id="stop-1-5",
            name="Universidad Autónoma",
            latitude=19.4420,
            longitude=-99.1100,
            distance_from_start=16.8,
            estimated_stop_duration=2
        ),
    ]
    
    route1 = Route(
        id="route-1",
        name="Ruta Centro - Universidad",
        stops=route1_stops,
        total_distance=16.8,
        estimated_duration=45
    )
    
    # Ruta 2: Aeropuerto - Centro
    route2_stops = [
        Stop(
            id="stop-2-1",
            name="Aeropuerto Internacional",
            latitude=19.4363,
            longitude=-99.0720,
            distance_from_start=0,
            estimated_stop_duration=3
        ),
        Stop(
            id="stop-2-2",
            name="Terminal de Autobuses",
            latitude=19.4340,
            longitude=-99.0900,
            distance_from_start=12.5,
            estimated_stop_duration=2
        ),
        Stop(
            id="stop-2-3",
            name="Estación de Metro",
            latitude=19.4330,
            longitude=-99.1100,
            distance_from_start=22.0,
            estimated_stop_duration=2
        ),
        Stop(
            id="stop-2-4",
            name="Centro Comercial",
            latitude=19.4320,
            longitude=-99.1300,
            distance_from_start=28.5,
            estimated_stop_duration=3
        ),
    ]
    
    route2 = Route(
        id="route-2",
        name="Ruta Aeropuerto - Centro",
        stops=route2_stops,
        total_distance=28.5,
        estimated_duration=60
    )
    
    # Ruta 3: Zona Residencial - Centro
    route3_stops = [
        Stop(
            id="stop-3-1",
            name="Residencial Norte",
            latitude=19.4500,
            longitude=-99.1400,
            distance_from_start=0,
            estimated_stop_duration=2
        ),
        Stop(
            id="stop-3-2",
            name="Mercado Municipal",
            latitude=19.4450,
            longitude=-99.1350,
            distance_from_start=6.0,
            estimated_stop_duration=3
        ),
        Stop(
            id="stop-3-3",
            name="Biblioteca Pública",
            latitude=19.4400,
            longitude=-99.1300,
            distance_from_start=11.5,
            estimated_stop_duration=2
        ),
        Stop(
            id="stop-3-4",
            name="Parque Central",
            latitude=19.4350,
            longitude=-99.1250,
            distance_from_start=16.0,
            estimated_stop_duration=2
        ),
        Stop(
            id="stop-3-5",
            name="Centro Histórico",
            latitude=19.4326,
            longitude=-99.1332,
            distance_from_start=20.5,
            estimated_stop_duration=3
        ),
    ]
    
    route3 = Route(
        id="route-3",
        name="Ruta Residencial - Centro",
        stops=route3_stops,
        total_distance=20.5,
        estimated_duration=50
    )
    
    return [route1, route2, route3]


def create_sample_transport_units():
    """Crear unidades de transporte de ejemplo."""
    
    now = datetime.now()
    
    units = [
        TransportUnit(
            id="unit-1",
            name="Autobús 101",
            route_id="route-1",
            current_location=Location(
                latitude=19.4330,
                longitude=-99.1300,
                route_progress=20.8,
                timestamp=now
            ),
            state=TransportState.EN_RUTA,
            speed=40,
            created_at=now,
            updated_at=now
        ),
        TransportUnit(
            id="unit-2",
            name="Autobús 202",
            route_id="route-2",
            current_location=Location(
                latitude=19.4340,
                longitude=-99.0900,
                route_progress=43.9,
                timestamp=now
            ),
            state=TransportState.EN_RUTA,
            speed=45,
            created_at=now,
            updated_at=now
        ),
        TransportUnit(
            id="unit-3",
            name="Autobús 303",
            route_id="route-3",
            current_location=Location(
                latitude=19.4400,
                longitude=-99.1300,
                route_progress=56.1,
                timestamp=now
            ),
            state=TransportState.DETENIDO,
            speed=0,
            created_at=now,
            updated_at=now
        ),
        TransportUnit(
            id="unit-4",
            name="Autobús 404",
            route_id="route-1",
            current_location=Location(
                latitude=19.4380,
                longitude=-99.1180,
                route_progress=68.5,
                timestamp=now
            ),
            state=TransportState.RETRASO,
            speed=35,
            created_at=now,
            updated_at=now
        ),
        TransportUnit(
            id="unit-5",
            name="Autobús 505",
            route_id="route-2",
            current_location=Location(
                latitude=19.4320,
                longitude=-99.1300,
                route_progress=100.0,
                timestamp=now
            ),
            state=TransportState.EN_RUTA,
            speed=0,
            created_at=now,
            updated_at=now
        ),
    ]
    
    return units


def seed_database(app, route_service, dashboard_service):
    """
    Cargar datos de ejemplo en la aplicación.
    
    Args:
        app: Aplicación Flask
        route_service: Servicio de rutas
        dashboard_service: Servicio de dashboard
    """
    print("Cargando datos de ejemplo...")
    
    # Crear y agregar rutas
    routes = create_sample_routes()
    for route in routes:
        route_service.add_route(route)
        print(f"✓ Ruta creada: {route.name} ({route.id})")
    
    # Crear y agregar unidades de transporte
    units = create_sample_transport_units()
    for unit in units:
        dashboard_service.add_transport_unit(unit)
        print(f"✓ Unidad creada: {unit.name} ({unit.id})")
    
    print(f"\n✓ {len(routes)} rutas cargadas")
    print(f"✓ {len(units)} unidades de transporte cargadas")
    print("\nDatos de ejemplo cargados exitosamente!")
    
    return routes, units
