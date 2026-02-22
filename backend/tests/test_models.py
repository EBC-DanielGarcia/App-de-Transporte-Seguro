"""
Tests unitarios para los modelos de datos.
"""

import pytest
from datetime import datetime
from models import (
    TransportUnit, Location, Route, Stop, TransportState,
    Delay, HistoryEvent, Metrics
)
from models.history_event import HistoryEventType


class TestLocation:
    """Tests para el modelo Location."""
    
    def test_location_creation(self, sample_location):
        """Verifica que se puede crear una ubicación."""
        assert sample_location.latitude == 25.6866
        assert sample_location.longitude == -100.3161
        assert sample_location.route_progress == 50.0
        assert isinstance(sample_location.timestamp, datetime)
    
    def test_location_to_dict(self, sample_location):
        """Verifica que se puede convertir una ubicación a diccionario."""
        location_dict = sample_location.to_dict()
        assert location_dict['latitude'] == 25.6866
        assert location_dict['longitude'] == -100.3161
        assert location_dict['route_progress'] == 50.0
        assert isinstance(location_dict['timestamp'], str)
    
    def test_location_from_dict(self, sample_location):
        """Verifica que se puede crear una ubicación desde un diccionario."""
        location_dict = sample_location.to_dict()
        restored_location = Location.from_dict(location_dict)
        assert restored_location.latitude == sample_location.latitude
        assert restored_location.longitude == sample_location.longitude
        assert restored_location.route_progress == sample_location.route_progress


class TestStop:
    """Tests para el modelo Stop."""
    
    def test_stop_creation(self, sample_stop):
        """Verifica que se puede crear una parada."""
        assert sample_stop.id == "stop_001"
        assert sample_stop.name == "Parada Central"
        assert sample_stop.latitude == 25.6866
        assert sample_stop.longitude == -100.3161
        assert sample_stop.distance_from_start == 5.0
        assert sample_stop.estimated_stop_duration == 60
    
    def test_stop_to_dict(self, sample_stop):
        """Verifica que se puede convertir una parada a diccionario."""
        stop_dict = sample_stop.to_dict()
        assert stop_dict['id'] == "stop_001"
        assert stop_dict['name'] == "Parada Central"
    
    def test_stop_from_dict(self, sample_stop):
        """Verifica que se puede crear una parada desde un diccionario."""
        stop_dict = sample_stop.to_dict()
        restored_stop = Stop.from_dict(stop_dict)
        assert restored_stop.id == sample_stop.id
        assert restored_stop.name == sample_stop.name


class TestRoute:
    """Tests para el modelo Route."""
    
    def test_route_creation(self, sample_route):
        """Verifica que se puede crear un recorrido."""
        assert sample_route.id == "route_001"
        assert sample_route.name == "Ruta Centro-Norte"
        assert len(sample_route.stops) == 3
        assert sample_route.total_distance == 10.0
        assert sample_route.estimated_duration == 30
    
    def test_route_to_dict(self, sample_route):
        """Verifica que se puede convertir un recorrido a diccionario."""
        route_dict = sample_route.to_dict()
        assert route_dict['id'] == "route_001"
        assert len(route_dict['stops']) == 3
    
    def test_route_from_dict(self, sample_route):
        """Verifica que se puede crear un recorrido desde un diccionario."""
        route_dict = sample_route.to_dict()
        restored_route = Route.from_dict(route_dict)
        assert restored_route.id == sample_route.id
        assert len(restored_route.stops) == len(sample_route.stops)


class TestTransportState:
    """Tests para el modelo TransportState."""
    
    def test_transport_state_values(self):
        """Verifica que los estados de transporte tienen los valores correctos."""
        assert TransportState.EN_RUTA.value == "En_Ruta"
        assert TransportState.DETENIDO.value == "Detenido"
        assert TransportState.RETRASO.value == "Retraso"
        assert TransportState.FUERA_SERVICIO.value == "Fuera_Servicio"
    
    def test_transport_state_string_conversion(self):
        """Verifica que se puede convertir un estado a string."""
        assert str(TransportState.EN_RUTA) == "En_Ruta"
        assert str(TransportState.DETENIDO) == "Detenido"


class TestTransportUnit:
    """Tests para el modelo TransportUnit."""
    
    def test_transport_unit_creation(self, sample_transport_unit):
        """Verifica que se puede crear una unidad de transporte."""
        assert sample_transport_unit.id == "unit_001"
        assert sample_transport_unit.name == "Autobús 101"
        assert sample_transport_unit.state == TransportState.EN_RUTA
        assert sample_transport_unit.speed == 40.0
    
    def test_transport_unit_to_dict(self, sample_transport_unit):
        """Verifica que se puede convertir una unidad a diccionario."""
        unit_dict = sample_transport_unit.to_dict()
        assert unit_dict['id'] == "unit_001"
        assert unit_dict['state'] == "En_Ruta"
        assert isinstance(unit_dict['created_at'], str)
    
    def test_transport_unit_from_dict(self, sample_transport_unit):
        """Verifica que se puede crear una unidad desde un diccionario."""
        unit_dict = sample_transport_unit.to_dict()
        restored_unit = TransportUnit.from_dict(unit_dict)
        assert restored_unit.id == sample_transport_unit.id
        assert restored_unit.state == sample_transport_unit.state


class TestDelay:
    """Tests para el modelo Delay."""
    
    def test_delay_creation(self, sample_delay):
        """Verifica que se puede crear un retraso."""
        assert sample_delay.id == "delay_001"
        assert sample_delay.transport_unit_id == "unit_001"
        assert sample_delay.magnitude == 15
        assert sample_delay.reason == "Tráfico intenso"
    
    def test_delay_to_dict(self, sample_delay):
        """Verifica que se puede convertir un retraso a diccionario."""
        delay_dict = sample_delay.to_dict()
        assert delay_dict['id'] == "delay_001"
        assert delay_dict['magnitude'] == 15
    
    def test_delay_from_dict(self, sample_delay):
        """Verifica que se puede crear un retraso desde un diccionario."""
        delay_dict = sample_delay.to_dict()
        restored_delay = Delay.from_dict(delay_dict)
        assert restored_delay.id == sample_delay.id
        assert restored_delay.magnitude == sample_delay.magnitude


class TestHistoryEvent:
    """Tests para el modelo HistoryEvent."""
    
    def test_history_event_creation(self, sample_history_event):
        """Verifica que se puede crear un evento de historial."""
        assert sample_history_event.id == "event_001"
        assert sample_history_event.transport_unit_id == "unit_001"
        assert sample_history_event.event_type == HistoryEventType.STATE_CHANGE
    
    def test_history_event_to_dict(self, sample_history_event):
        """Verifica que se puede convertir un evento a diccionario."""
        event_dict = sample_history_event.to_dict()
        assert event_dict['id'] == "event_001"
        assert event_dict['event_type'] == "STATE_CHANGE"
    
    def test_history_event_from_dict(self, sample_history_event):
        """Verifica que se puede crear un evento desde un diccionario."""
        event_dict = sample_history_event.to_dict()
        restored_event = HistoryEvent.from_dict(event_dict)
        assert restored_event.id == sample_history_event.id
        assert restored_event.event_type == sample_history_event.event_type


class TestMetrics:
    """Tests para el modelo Metrics."""
    
    def test_metrics_creation(self, sample_metrics):
        """Verifica que se puede crear un objeto de métricas."""
        assert sample_metrics.transport_unit_id == "unit_001"
        assert sample_metrics.total_travel_time == 45
        assert sample_metrics.total_delay_time == 15
        assert sample_metrics.delay_count == 2
        assert sample_metrics.average_delay == 7.5
        assert sample_metrics.on_time_percentage == 66.7
    
    def test_metrics_to_dict(self, sample_metrics):
        """Verifica que se puede convertir métricas a diccionario."""
        metrics_dict = sample_metrics.to_dict()
        assert metrics_dict['transport_unit_id'] == "unit_001"
        assert metrics_dict['total_travel_time'] == 45
    
    def test_metrics_from_dict(self, sample_metrics):
        """Verifica que se puede crear métricas desde un diccionario."""
        metrics_dict = sample_metrics.to_dict()
        restored_metrics = Metrics.from_dict(metrics_dict)
        assert restored_metrics.transport_unit_id == sample_metrics.transport_unit_id
        assert restored_metrics.total_travel_time == sample_metrics.total_travel_time
