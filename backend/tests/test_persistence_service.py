"""
Tests unitarios para el servicio de persistencia.
"""

import pytest
from datetime import datetime, timedelta
from services.persistence_service import PersistenceService
from models import Location, TransportState, Delay, HistoryEvent
from models.history_event import HistoryEventType


class TestPersistenceServiceLocationUpdate:
    """Tests para guardar y recuperar actualizaciones de ubicación."""
    
    def test_save_location_update(self, sample_location):
        """Verifica que se puede guardar una ubicación."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        service.save_location_update(transport_unit_id, sample_location)
        
        locations = service.get_location_history(transport_unit_id)
        assert len(locations) == 1
        assert locations[0].latitude == sample_location.latitude
        assert locations[0].longitude == sample_location.longitude
    
    def test_save_multiple_location_updates(self, sample_location):
        """Verifica que se pueden guardar múltiples ubicaciones."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        # Guardar primera ubicación
        service.save_location_update(transport_unit_id, sample_location)
        
        # Guardar segunda ubicación con progreso diferente
        location2 = Location(
            latitude=25.7000,
            longitude=-100.3200,
            route_progress=75.0,
            timestamp=datetime.now()
        )
        service.save_location_update(transport_unit_id, location2)
        
        locations = service.get_location_history(transport_unit_id)
        assert len(locations) == 2
        assert locations[0].route_progress == 50.0
        assert locations[1].route_progress == 75.0
    
    def test_location_history_ordered_by_timestamp(self):
        """Verifica que el historial de ubicaciones está ordenado por timestamp."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        now = datetime.now()
        
        # Guardar ubicaciones en orden inverso
        location3 = Location(
            latitude=25.7000,
            longitude=-100.3200,
            route_progress=75.0,
            timestamp=now + timedelta(seconds=2)
        )
        location1 = Location(
            latitude=25.6866,
            longitude=-100.3161,
            route_progress=50.0,
            timestamp=now
        )
        location2 = Location(
            latitude=25.6900,
            longitude=-100.3180,
            route_progress=60.0,
            timestamp=now + timedelta(seconds=1)
        )
        
        service.save_location_update(transport_unit_id, location3)
        service.save_location_update(transport_unit_id, location1)
        service.save_location_update(transport_unit_id, location2)
        
        locations = service.get_location_history(transport_unit_id)
        assert len(locations) == 3
        assert locations[0].route_progress == 50.0
        assert locations[1].route_progress == 60.0
        assert locations[2].route_progress == 75.0
    
    def test_get_location_history_empty(self):
        """Verifica que retorna lista vacía si no hay ubicaciones."""
        service = PersistenceService()
        locations = service.get_location_history("unit_nonexistent")
        assert locations == []


class TestPersistenceServiceStateChange:
    """Tests para guardar y recuperar cambios de estado."""
    
    def test_save_state_change(self):
        """Verifica que se puede guardar un cambio de estado."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        service.save_state_change(
            transport_unit_id,
            TransportState.EN_RUTA,
            TransportState.DETENIDO
        )
        
        state_changes = service.get_state_change_history(transport_unit_id)
        assert len(state_changes) == 1
        assert state_changes[0].event_type == HistoryEventType.STATE_CHANGE
        assert state_changes[0].data["new_state"] == "En_Ruta"
        assert state_changes[0].data["old_state"] == "Detenido"
    
    def test_save_multiple_state_changes(self):
        """Verifica que se pueden guardar múltiples cambios de estado."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        service.save_state_change(transport_unit_id, TransportState.EN_RUTA)
        service.save_state_change(transport_unit_id, TransportState.DETENIDO, TransportState.EN_RUTA)
        service.save_state_change(transport_unit_id, TransportState.RETRASO, TransportState.DETENIDO)
        
        state_changes = service.get_state_change_history(transport_unit_id)
        assert len(state_changes) == 3
        assert state_changes[0].data["new_state"] == "En_Ruta"
        assert state_changes[1].data["new_state"] == "Detenido"
        assert state_changes[2].data["new_state"] == "Retraso"
    
    def test_state_change_has_timestamp(self):
        """Verifica que cada cambio de estado tiene timestamp."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        before = datetime.now()
        service.save_state_change(transport_unit_id, TransportState.EN_RUTA)
        after = datetime.now()
        
        state_changes = service.get_state_change_history(transport_unit_id)
        assert len(state_changes) == 1
        assert before <= state_changes[0].timestamp <= after
    
    def test_get_state_change_history_empty(self):
        """Verifica que retorna lista vacía si no hay cambios de estado."""
        service = PersistenceService()
        state_changes = service.get_state_change_history("unit_nonexistent")
        assert state_changes == []


class TestPersistenceServiceDelayEvent:
    """Tests para guardar y recuperar eventos de retraso."""
    
    def test_save_delay_event(self, sample_delay):
        """Verifica que se puede guardar un evento de retraso."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        service.save_delay_event(transport_unit_id, sample_delay)
        
        delays = service.get_delay_history(transport_unit_id)
        assert len(delays) == 1
        assert delays[0].id == sample_delay.id
        assert delays[0].magnitude == sample_delay.magnitude
    
    def test_save_multiple_delay_events(self, sample_stop):
        """Verifica que se pueden guardar múltiples eventos de retraso."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        now = datetime.now()
        
        delay1 = Delay(
            id="delay_001",
            transport_unit_id=transport_unit_id,
            detected_at=now,
            magnitude=10,
            affected_stop=sample_stop,
            reason="Tráfico"
        )
        
        delay2 = Delay(
            id="delay_002",
            transport_unit_id=transport_unit_id,
            detected_at=now + timedelta(minutes=5),
            magnitude=15,
            affected_stop=sample_stop,
            reason="Accidente"
        )
        
        service.save_delay_event(transport_unit_id, delay1)
        service.save_delay_event(transport_unit_id, delay2)
        
        delays = service.get_delay_history(transport_unit_id)
        assert len(delays) == 2
        assert delays[0].magnitude == 10
        assert delays[1].magnitude == 15
    
    def test_delay_history_ordered_by_timestamp(self, sample_stop):
        """Verifica que el historial de retrasos está ordenado por timestamp."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        now = datetime.now()
        
        delay3 = Delay(
            id="delay_003",
            transport_unit_id=transport_unit_id,
            detected_at=now + timedelta(minutes=10),
            magnitude=20,
            affected_stop=sample_stop
        )
        
        delay1 = Delay(
            id="delay_001",
            transport_unit_id=transport_unit_id,
            detected_at=now,
            magnitude=10,
            affected_stop=sample_stop
        )
        
        delay2 = Delay(
            id="delay_002",
            transport_unit_id=transport_unit_id,
            detected_at=now + timedelta(minutes=5),
            magnitude=15,
            affected_stop=sample_stop
        )
        
        # Guardar en orden inverso
        service.save_delay_event(transport_unit_id, delay3)
        service.save_delay_event(transport_unit_id, delay1)
        service.save_delay_event(transport_unit_id, delay2)
        
        delays = service.get_delay_history(transport_unit_id)
        assert len(delays) == 3
        assert delays[0].magnitude == 10
        assert delays[1].magnitude == 15
        assert delays[2].magnitude == 20
    
    def test_get_delay_history_empty(self):
        """Verifica que retorna lista vacía si no hay retrasos."""
        service = PersistenceService()
        delays = service.get_delay_history("unit_nonexistent")
        assert delays == []


class TestPersistenceServiceHistory:
    """Tests para el historial completo de eventos."""
    
    def test_get_history_includes_all_event_types(self, sample_location, sample_delay):
        """Verifica que el historial incluye todos los tipos de eventos."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        # Guardar diferentes tipos de eventos
        service.save_location_update(transport_unit_id, sample_location)
        service.save_state_change(transport_unit_id, TransportState.EN_RUTA)
        service.save_delay_event(transport_unit_id, sample_delay)
        
        history = service.get_history(transport_unit_id)
        assert len(history) == 3
        
        # Verificar que hay eventos de cada tipo
        event_types = {event.event_type for event in history}
        assert HistoryEventType.LOCATION_UPDATE in event_types
        assert HistoryEventType.STATE_CHANGE in event_types
        assert HistoryEventType.DELAY_DETECTED in event_types
    
    def test_history_ordered_chronologically(self, sample_location, sample_stop):
        """Verifica que el historial está ordenado cronológicamente."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        now = datetime.now()
        
        # Crear eventos con timestamps específicos
        location = Location(
            latitude=25.6866,
            longitude=-100.3161,
            route_progress=50.0,
            timestamp=now
        )
        
        delay = Delay(
            id="delay_001",
            transport_unit_id=transport_unit_id,
            detected_at=now + timedelta(seconds=10),
            magnitude=15,
            affected_stop=sample_stop
        )
        
        # Guardar en orden inverso
        service.save_delay_event(transport_unit_id, delay)
        service.save_location_update(transport_unit_id, location)
        
        history = service.get_history(transport_unit_id)
        assert len(history) == 2
        assert history[0].timestamp <= history[1].timestamp
    
    def test_get_history_empty(self):
        """Verifica que retorna lista vacía si no hay historial."""
        service = PersistenceService()
        history = service.get_history("unit_nonexistent")
        assert history == []


class TestPersistenceServiceMetrics:
    """Tests para el cálculo de métricas."""
    
    def test_get_metrics_no_delays(self):
        """Verifica cálculo de métricas sin retrasos."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        now = datetime.now()
        
        # Guardar ubicaciones para calcular tiempo de viaje
        location1 = Location(
            latitude=25.6866,
            longitude=-100.3161,
            route_progress=0.0,
            timestamp=now
        )
        
        location2 = Location(
            latitude=25.7000,
            longitude=-100.3200,
            route_progress=100.0,
            timestamp=now + timedelta(minutes=30)
        )
        
        service.save_location_update(transport_unit_id, location1)
        service.save_location_update(transport_unit_id, location2)
        
        metrics = service.get_metrics(transport_unit_id)
        
        assert metrics.transport_unit_id == transport_unit_id
        assert metrics.total_travel_time == 30
        assert metrics.total_delay_time == 0
        assert metrics.delay_count == 0
        assert metrics.average_delay == 0.0
        assert metrics.on_time_percentage == 100.0
    
    def test_get_metrics_with_delays(self, sample_stop):
        """Verifica cálculo de métricas con retrasos."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        now = datetime.now()
        
        # Guardar ubicaciones
        location1 = Location(
            latitude=25.6866,
            longitude=-100.3161,
            route_progress=0.0,
            timestamp=now
        )
        
        location2 = Location(
            latitude=25.7000,
            longitude=-100.3200,
            route_progress=100.0,
            timestamp=now + timedelta(minutes=45)
        )
        
        service.save_location_update(transport_unit_id, location1)
        service.save_location_update(transport_unit_id, location2)
        
        # Guardar retrasos
        delay1 = Delay(
            id="delay_001",
            transport_unit_id=transport_unit_id,
            detected_at=now + timedelta(minutes=10),
            magnitude=10,
            affected_stop=sample_stop
        )
        
        delay2 = Delay(
            id="delay_002",
            transport_unit_id=transport_unit_id,
            detected_at=now + timedelta(minutes=20),
            magnitude=5,
            affected_stop=sample_stop
        )
        
        service.save_delay_event(transport_unit_id, delay1)
        service.save_delay_event(transport_unit_id, delay2)
        
        metrics = service.get_metrics(transport_unit_id)
        
        assert metrics.total_travel_time == 45
        assert metrics.total_delay_time == 15
        assert metrics.delay_count == 2
        assert metrics.average_delay == 7.5
        assert metrics.on_time_percentage == 66.7
    
    def test_get_metrics_single_location(self, sample_location):
        """Verifica cálculo de métricas con una sola ubicación."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        service.save_location_update(transport_unit_id, sample_location)
        
        metrics = service.get_metrics(transport_unit_id)
        
        assert metrics.total_travel_time == 0
        assert metrics.total_delay_time == 0
        assert metrics.delay_count == 0
        assert metrics.average_delay == 0.0
        assert metrics.on_time_percentage == 0.0
    
    def test_get_metrics_no_data(self):
        """Verifica cálculo de métricas sin datos."""
        service = PersistenceService()
        
        metrics = service.get_metrics("unit_nonexistent")
        
        assert metrics.transport_unit_id == "unit_nonexistent"
        assert metrics.total_travel_time == 0
        assert metrics.total_delay_time == 0
        assert metrics.delay_count == 0
        assert metrics.average_delay == 0.0
        assert metrics.on_time_percentage == 0.0


class TestPersistenceServiceClearHistory:
    """Tests para limpiar el historial."""
    
    def test_clear_history(self, sample_location, sample_delay):
        """Verifica que se puede limpiar el historial."""
        service = PersistenceService()
        transport_unit_id = "unit_001"
        
        # Guardar datos
        service.save_location_update(transport_unit_id, sample_location)
        service.save_state_change(transport_unit_id, TransportState.EN_RUTA)
        service.save_delay_event(transport_unit_id, sample_delay)
        
        # Verificar que hay datos
        assert len(service.get_history(transport_unit_id)) == 3
        
        # Limpiar historial
        service.clear_history(transport_unit_id)
        
        # Verificar que está vacío
        assert len(service.get_history(transport_unit_id)) == 0
        assert len(service.get_location_history(transport_unit_id)) == 0
        assert len(service.get_state_change_history(transport_unit_id)) == 0
        assert len(service.get_delay_history(transport_unit_id)) == 0
    
    def test_clear_history_does_not_affect_other_units(self, sample_location):
        """Verifica que limpiar historial de una unidad no afecta otras."""
        service = PersistenceService()
        
        # Guardar datos para dos unidades
        service.save_location_update("unit_001", sample_location)
        service.save_location_update("unit_002", sample_location)
        
        # Limpiar historial de unit_001
        service.clear_history("unit_001")
        
        # Verificar que unit_001 está vacío pero unit_002 no
        assert len(service.get_location_history("unit_001")) == 0
        assert len(service.get_location_history("unit_002")) == 1


class TestPersistenceServiceMultipleUnits:
    """Tests para manejo de múltiples unidades de transporte."""
    
    def test_separate_storage_per_unit(self, sample_location):
        """Verifica que cada unidad tiene almacenamiento separado."""
        service = PersistenceService()
        
        service.save_location_update("unit_001", sample_location)
        service.save_location_update("unit_002", sample_location)
        
        locations_unit1 = service.get_location_history("unit_001")
        locations_unit2 = service.get_location_history("unit_002")
        
        assert len(locations_unit1) == 1
        assert len(locations_unit2) == 1
    
    def test_independent_metrics_per_unit(self, sample_stop):
        """Verifica que las métricas son independientes por unidad."""
        service = PersistenceService()
        
        now = datetime.now()
        
        # Crear ubicaciones para unit_001
        location1_unit1 = Location(
            latitude=25.6866,
            longitude=-100.3161,
            route_progress=0.0,
            timestamp=now
        )
        
        location2_unit1 = Location(
            latitude=25.7000,
            longitude=-100.3200,
            route_progress=100.0,
            timestamp=now + timedelta(minutes=30)
        )
        
        # Crear ubicaciones para unit_002
        location1_unit2 = Location(
            latitude=25.6866,
            longitude=-100.3161,
            route_progress=0.0,
            timestamp=now
        )
        
        location2_unit2 = Location(
            latitude=25.7000,
            longitude=-100.3200,
            route_progress=100.0,
            timestamp=now + timedelta(minutes=60)
        )
        
        service.save_location_update("unit_001", location1_unit1)
        service.save_location_update("unit_001", location2_unit1)
        service.save_location_update("unit_002", location1_unit2)
        service.save_location_update("unit_002", location2_unit2)
        
        # Guardar retraso solo para unit_001
        delay = Delay(
            id="delay_001",
            transport_unit_id="unit_001",
            detected_at=now + timedelta(minutes=10),
            magnitude=10,
            affected_stop=sample_stop
        )
        service.save_delay_event("unit_001", delay)
        
        metrics_unit1 = service.get_metrics("unit_001")
        metrics_unit2 = service.get_metrics("unit_002")
        
        assert metrics_unit1.total_travel_time == 30
        assert metrics_unit1.total_delay_time == 10
        assert metrics_unit2.total_travel_time == 60
        assert metrics_unit2.total_delay_time == 0
