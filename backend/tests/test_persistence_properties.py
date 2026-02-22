"""
Pruebas de propiedad para el servicio de persistencia.

Estas pruebas validan propiedades universales que deben cumplirse
para todos los inputs válidos usando property-based testing con Hypothesis.
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, assume
from services.persistence_service import PersistenceService
from models import Location, TransportState, Delay
from models.stop import Stop


# Estrategias personalizadas para generar datos válidos

@st.composite
def transport_unit_ids(draw):
    """Genera IDs de unidades de transporte válidos."""
    return draw(st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'))


@st.composite
def valid_locations(draw):
    """Genera ubicaciones válidas."""
    return Location(
        latitude=draw(st.floats(min_value=-90, max_value=90)),
        longitude=draw(st.floats(min_value=-180, max_value=180)),
        route_progress=draw(st.floats(min_value=0, max_value=100)),
        timestamp=datetime.now()
    )


@st.composite
def valid_stops(draw):
    """Genera paradas válidas."""
    return Stop(
        id=draw(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_')),
        name=draw(st.text(min_size=1, max_size=50)),
        latitude=draw(st.floats(min_value=-90, max_value=90)),
        longitude=draw(st.floats(min_value=-180, max_value=180)),
        distance_from_start=draw(st.floats(min_value=0, max_value=1000)),
        estimated_stop_duration=draw(st.integers(min_value=1, max_value=300))
    )


@st.composite
def valid_delays(draw, transport_unit_id):
    """Genera retrasos válidos."""
    return Delay(
        id=draw(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_')),
        transport_unit_id=transport_unit_id,
        detected_at=datetime.now(),
        magnitude=draw(st.integers(min_value=1, max_value=300)),
        affected_stop=draw(valid_stops()),
        reason=draw(st.one_of(st.none(), st.text(max_size=100)))
    )


class TestProperty19StateChangePersistence:
    """
    Property 19: State Change Persistence
    
    **Validates: Requirements 9.1**
    
    Para cualquier cambio de estado, el sistema debe persistir el cambio
    inmediatamente y recuperarlo correctamente después.
    """
    
    @given(
        transport_unit_id=transport_unit_ids(),
        state=st.sampled_from(TransportState)
    )
    def test_state_change_persistence_round_trip(self, transport_unit_id, state):
        """
        Propiedad: Para cualquier cambio de estado, el sistema debe persistir
        el cambio y recuperarlo correctamente.
        
        Genera cambios de estado aleatorios y verifica que:
        1. Se puede guardar el cambio
        2. Se puede recuperar el cambio
        3. El estado recuperado es idéntico al guardado
        """
        service = PersistenceService()
        
        # Guardar cambio de estado
        service.save_state_change(transport_unit_id, state)
        
        # Recuperar cambio de estado
        state_changes = service.get_state_change_history(transport_unit_id)
        
        # Verificar que se recuperó correctamente
        assert len(state_changes) == 1
        assert state_changes[0].data["new_state"] == str(state)
    
    @given(
        transport_unit_id=transport_unit_ids(),
        states=st.lists(st.sampled_from(TransportState), min_size=1, max_size=10)
    )
    def test_multiple_state_changes_persistence(self, transport_unit_id, states):
        """
        Propiedad: Para múltiples cambios de estado, todos deben persistirse
        y recuperarse en el orden correcto.
        
        Genera múltiples cambios de estado y verifica que:
        1. Se guardan todos los cambios
        2. Se recuperan en el orden correcto
        3. Cada cambio tiene el estado correcto
        """
        service = PersistenceService()
        
        # Guardar múltiples cambios de estado
        for state in states:
            service.save_state_change(transport_unit_id, state)
        
        # Recuperar cambios de estado
        state_changes = service.get_state_change_history(transport_unit_id)
        
        # Verificar que se recuperaron todos
        assert len(state_changes) == len(states)
        
        # Verificar que cada cambio tiene el estado correcto
        for i, state in enumerate(states):
            assert state_changes[i].data["new_state"] == str(state)
    
    @given(
        transport_unit_id=transport_unit_ids(),
        state=st.sampled_from(TransportState)
    )
    def test_state_change_has_timestamp(self, transport_unit_id, state):
        """
        Propiedad: Cada cambio de estado debe tener un timestamp válido.
        
        Verifica que:
        1. El timestamp existe
        2. El timestamp es una instancia de datetime
        3. El timestamp es cercano al tiempo actual
        """
        service = PersistenceService()
        
        before = datetime.now()
        service.save_state_change(transport_unit_id, state)
        after = datetime.now()
        
        state_changes = service.get_state_change_history(transport_unit_id)
        
        assert len(state_changes) == 1
        assert isinstance(state_changes[0].timestamp, datetime)
        assert before <= state_changes[0].timestamp <= after


class TestProperty20LocationPersistenceRoundTrip:
    """
    Property 20: Location Persistence Round-trip
    
    **Validates: Requirements 9.2, 9.4**
    
    Para cualquier actualización de ubicación, el sistema debe persistir
    la ubicación con timestamp y recuperar exactamente los mismos datos.
    """
    
    @given(location=valid_locations(), transport_unit_id=transport_unit_ids())
    def test_location_persistence_round_trip(self, location, transport_unit_id):
        """
        Propiedad: Para cualquier ubicación, el sistema debe persistir
        la ubicación y recuperarla exactamente igual.
        
        Genera ubicaciones aleatorias y verifica que:
        1. Se puede guardar la ubicación
        2. Se puede recuperar la ubicación
        3. Los datos recuperados son idénticos a los guardados
        """
        service = PersistenceService()
        
        # Guardar ubicación
        service.save_location_update(transport_unit_id, location)
        
        # Recuperar ubicación
        locations = service.get_location_history(transport_unit_id)
        
        # Verificar que se recuperó correctamente
        assert len(locations) == 1
        assert locations[0].latitude == location.latitude
        assert locations[0].longitude == location.longitude
        assert locations[0].route_progress == location.route_progress
    
    @given(
        locations=st.lists(valid_locations(), min_size=1, max_size=20),
        transport_unit_id=transport_unit_ids()
    )
    def test_multiple_locations_persistence(self, locations, transport_unit_id):
        """
        Propiedad: Para múltiples ubicaciones, todas deben persistirse
        y recuperarse en orden cronológico.
        
        Genera múltiples ubicaciones y verifica que:
        1. Se guardan todas las ubicaciones
        2. Se recuperan en orden cronológico
        3. Cada ubicación tiene los datos correctos
        """
        service = PersistenceService()
        
        # Guardar múltiples ubicaciones
        for location in locations:
            service.save_location_update(transport_unit_id, location)
        
        # Recuperar ubicaciones
        recovered_locations = service.get_location_history(transport_unit_id)
        
        # Verificar que se recuperaron todas
        assert len(recovered_locations) == len(locations)
        
        # Verificar que están ordenadas por timestamp
        for i in range(len(recovered_locations) - 1):
            assert recovered_locations[i].timestamp <= recovered_locations[i + 1].timestamp
    
    @given(location=valid_locations(), transport_unit_id=transport_unit_ids())
    def test_location_has_timestamp(self, location, transport_unit_id):
        """
        Propiedad: Cada ubicación persistida debe tener un timestamp válido.
        
        Verifica que:
        1. El timestamp existe
        2. El timestamp es una instancia de datetime
        3. El timestamp es el mismo que se guardó
        """
        service = PersistenceService()
        
        service.save_location_update(transport_unit_id, location)
        
        locations = service.get_location_history(transport_unit_id)
        
        assert len(locations) == 1
        assert isinstance(locations[0].timestamp, datetime)
        assert locations[0].timestamp == location.timestamp


class TestProperty21DelayEventPersistence:
    """
    Property 21: Delay Event Persistence
    
    **Validates: Requirements 9.3**
    
    Para cualquier evento de retraso detectado, el sistema debe persistir
    el retraso en el historial y recuperarlo cuando se acceda a datos históricos.
    """
    
    @given(
        transport_unit_id=transport_unit_ids(),
        delay=st.builds(
            Delay,
            id=st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'),
            transport_unit_id=st.just("unit_test"),
            detected_at=st.just(datetime.now()),
            magnitude=st.integers(min_value=1, max_value=300),
            affected_stop=valid_stops(),
            reason=st.one_of(st.none(), st.text(max_size=100))
        )
    )
    def test_delay_event_persistence_round_trip(self, transport_unit_id, delay):
        """
        Propiedad: Para cualquier evento de retraso, el sistema debe persistir
        el retraso y recuperarlo exactamente igual.
        
        Genera retrasos aleatorios y verifica que:
        1. Se puede guardar el retraso
        2. Se puede recuperar el retraso
        3. Los datos recuperados son idénticos a los guardados
        """
        service = PersistenceService()
        
        # Actualizar transport_unit_id del delay
        delay.transport_unit_id = transport_unit_id
        
        # Guardar retraso
        service.save_delay_event(transport_unit_id, delay)
        
        # Recuperar retraso
        delays = service.get_delay_history(transport_unit_id)
        
        # Verificar que se recuperó correctamente
        assert len(delays) == 1
        assert delays[0].id == delay.id
        assert delays[0].magnitude == delay.magnitude
        assert delays[0].transport_unit_id == delay.transport_unit_id
    
    @given(
        transport_unit_id=transport_unit_ids(),
        delay_magnitudes=st.lists(st.integers(min_value=1, max_value=300), min_size=1, max_size=10)
    )
    def test_multiple_delay_events_persistence(self, transport_unit_id, delay_magnitudes):
        """
        Propiedad: Para múltiples eventos de retraso, todos deben persistirse
        y recuperarse en orden cronológico.
        
        Genera múltiples retrasos y verifica que:
        1. Se guardan todos los retrasos
        2. Se recuperan en orden cronológico
        3. Cada retraso tiene la magnitud correcta
        """
        service = PersistenceService()
        
        now = datetime.now()
        
        # Guardar múltiples retrasos
        for i, magnitude in enumerate(delay_magnitudes):
            delay = Delay(
                id=f"delay_{i}",
                transport_unit_id=transport_unit_id,
                detected_at=now + timedelta(seconds=i),
                magnitude=magnitude,
                affected_stop=Stop(
                    id="stop_001",
                    name="Test Stop",
                    latitude=25.0,
                    longitude=-100.0,
                    distance_from_start=0.0,
                    estimated_stop_duration=60
                )
            )
            service.save_delay_event(transport_unit_id, delay)
        
        # Recuperar retrasos
        delays = service.get_delay_history(transport_unit_id)
        
        # Verificar que se recuperaron todos
        assert len(delays) == len(delay_magnitudes)
        
        # Verificar que están ordenados por timestamp
        for i in range(len(delays) - 1):
            assert delays[i].detected_at <= delays[i + 1].detected_at
        
        # Verificar que cada retraso tiene la magnitud correcta
        for i, magnitude in enumerate(delay_magnitudes):
            assert delays[i].magnitude == magnitude
    
    @given(
        transport_unit_id=transport_unit_ids(),
        delay=st.builds(
            Delay,
            id=st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'),
            transport_unit_id=st.just("unit_test"),
            detected_at=st.just(datetime.now()),
            magnitude=st.integers(min_value=1, max_value=300),
            affected_stop=valid_stops(),
            reason=st.one_of(st.none(), st.text(max_size=100))
        )
    )
    def test_delay_event_in_history(self, transport_unit_id, delay):
        """
        Propiedad: Cada evento de retraso persistido debe aparecer en el historial.
        
        Verifica que:
        1. El retraso se guarda
        2. El retraso aparece en el historial general
        3. El retraso tiene el tipo de evento correcto
        """
        service = PersistenceService()
        
        # Actualizar transport_unit_id del delay
        delay.transport_unit_id = transport_unit_id
        
        # Guardar retraso
        service.save_delay_event(transport_unit_id, delay)
        
        # Recuperar historial
        history = service.get_history(transport_unit_id)
        
        # Verificar que el retraso está en el historial
        assert len(history) >= 1
        
        # Buscar el evento de retraso
        delay_events = [e for e in history if e.event_type.value == "DELAY_DETECTED"]
        assert len(delay_events) >= 1


class TestPersistenceIntegration:
    """
    Tests de integración para verificar que la persistencia funciona
    correctamente con múltiples tipos de eventos.
    """
    
    @given(
        transport_unit_id=transport_unit_ids(),
        locations=st.lists(valid_locations(), min_size=1, max_size=5),
        states=st.lists(st.sampled_from(TransportState), min_size=1, max_size=5)
    )
    def test_mixed_events_persistence(self, transport_unit_id, locations, states):
        """
        Propiedad: Cuando se guardan múltiples tipos de eventos,
        todos deben persistirse y recuperarse correctamente.
        """
        service = PersistenceService()
        
        # Guardar ubicaciones
        for location in locations:
            service.save_location_update(transport_unit_id, location)
        
        # Guardar cambios de estado
        for state in states:
            service.save_state_change(transport_unit_id, state)
        
        # Verificar que se recuperan todos los eventos
        history = service.get_history(transport_unit_id)
        assert len(history) == len(locations) + len(states)
        
        # Verificar que hay eventos de cada tipo
        location_events = [e for e in history if e.event_type.value == "LOCATION_UPDATE"]
        state_events = [e for e in history if e.event_type.value == "STATE_CHANGE"]
        
        assert len(location_events) == len(locations)
        assert len(state_events) == len(states)
    
    @given(
        transport_unit_id=transport_unit_ids(),
        location=valid_locations()
    )
    def test_metrics_calculation_consistency(self, transport_unit_id, location):
        """
        Propiedad: Las métricas calculadas deben ser consistentes
        con los datos persistidos.
        """
        service = PersistenceService()
        
        # Guardar ubicación
        service.save_location_update(transport_unit_id, location)
        
        # Calcular métricas
        metrics = service.get_metrics(transport_unit_id)
        
        # Verificar que las métricas son válidas
        assert metrics.transport_unit_id == transport_unit_id
        assert metrics.total_delay_time >= 0
        assert metrics.delay_count >= 0
        assert metrics.average_delay >= 0
        assert 0 <= metrics.on_time_percentage <= 100
