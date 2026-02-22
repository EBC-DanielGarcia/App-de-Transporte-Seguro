"""
Configuración compartida para tests usando pytest.
"""

import pytest
from datetime import datetime
from models import (
    TransportUnit, Location, Route, Stop, TransportState,
    Delay, HistoryEvent, Metrics
)
from models.history_event import HistoryEventType


@pytest.fixture
def sample_location():
    """Fixture que proporciona una ubicación de ejemplo."""
    return Location(
        latitude=25.6866,
        longitude=-100.3161,
        route_progress=50.0,
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_stop():
    """Fixture que proporciona una parada de ejemplo."""
    return Stop(
        id="stop_001",
        name="Parada Central",
        latitude=25.6866,
        longitude=-100.3161,
        distance_from_start=5.0,
        estimated_stop_duration=60
    )


@pytest.fixture
def sample_stops():
    """Fixture que proporciona múltiples paradas de ejemplo."""
    return [
        Stop(
            id="stop_001",
            name="Parada Central",
            latitude=25.6866,
            longitude=-100.3161,
            distance_from_start=0.0,
            estimated_stop_duration=60
        ),
        Stop(
            id="stop_002",
            name="Parada Norte",
            latitude=25.7000,
            longitude=-100.3200,
            distance_from_start=5.0,
            estimated_stop_duration=45
        ),
        Stop(
            id="stop_003",
            name="Parada Sur",
            latitude=25.6700,
            longitude=-100.3100,
            distance_from_start=10.0,
            estimated_stop_duration=45
        ),
    ]


@pytest.fixture
def sample_route(sample_stops):
    """Fixture que proporciona un recorrido de ejemplo."""
    return Route(
        id="route_001",
        name="Ruta Centro-Norte",
        stops=sample_stops,
        total_distance=10.0,
        estimated_duration=30
    )


@pytest.fixture
def sample_transport_unit(sample_location, sample_route):
    """Fixture que proporciona una unidad de transporte de ejemplo."""
    now = datetime.now()
    return TransportUnit(
        id="unit_001",
        name="Autobús 101",
        route_id=sample_route.id,
        current_location=sample_location,
        state=TransportState.EN_RUTA,
        speed=40.0,
        created_at=now,
        updated_at=now
    )


@pytest.fixture
def sample_delay(sample_stop):
    """Fixture que proporciona un retraso de ejemplo."""
    return Delay(
        id="delay_001",
        transport_unit_id="unit_001",
        detected_at=datetime.now(),
        magnitude=15,
        affected_stop=sample_stop,
        reason="Tráfico intenso"
    )


@pytest.fixture
def sample_history_event():
    """Fixture que proporciona un evento de historial de ejemplo."""
    return HistoryEvent(
        id="event_001",
        transport_unit_id="unit_001",
        event_type=HistoryEventType.STATE_CHANGE,
        timestamp=datetime.now(),
        data={"old_state": "En_Ruta", "new_state": "Detenido"}
    )


@pytest.fixture
def sample_metrics():
    """Fixture que proporciona métricas de ejemplo."""
    return Metrics(
        transport_unit_id="unit_001",
        total_travel_time=45,
        total_delay_time=15,
        delay_count=2,
        average_delay=7.5,
        on_time_percentage=66.7
    )
