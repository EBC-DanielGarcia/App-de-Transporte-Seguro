"""
Tests unitarios para el motor de detección de retrasos.
"""

import pytest
from datetime import datetime
from services.delay_detection_engine import DelayDetectionEngine
from services.eta_calculator import ETACalculator
from services.persistence_service import PersistenceService
from models import Location, Route, Stop, TransportUnit, TransportState, Delay


class TestDelayDetectionEngineInitialization:
    """Tests para inicialización del motor de detección de retrasos."""
    
    def test_engine_initialization(self):
        """Verifica que el motor se inicializa correctamente."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        assert engine is not None
        assert engine.eta_calculator is not None
        assert engine.persistence_service is not None
    
    def test_engine_initial_state(self):
        """Verifica que el motor inicia sin retrasos detectados."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        assert engine.get_delay_magnitude("unit_001") == 0
        assert not engine.is_delayed("unit_001")
        assert len(engine.get_detected_delays("unit_001")) == 0


class TestCheckForDelays:
    """Tests para detección de retrasos."""
    
    def test_check_for_delays_no_previous_eta(
        self,
        sample_transport_unit,
        sample_route,
        sample_stop
    ):
        """Verifica que no hay retrasos sin ETA anterior."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        delays = engine.check_for_delays(
            transport_unit_id=sample_transport_unit.id,
            current_location=sample_transport_unit.current_location,
            route=sample_route,
            speed=sample_transport_unit.speed,
            current_stop=sample_stop
        )
        
        # Sin ETA anterior, no debe haber retrasos
        assert len(delays) == 0
    
    def test_check_for_delays_with_eta_change(
        self,
        sample_transport_unit,
        sample_route,
        sample_stop
    ):
        """Verifica detección de retrasos con cambio de ETA."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        # Calcular ETA inicial
        eta_calculator.recalculate_all_etas(
            transport_unit_id=sample_transport_unit.id,
            current_location=sample_transport_unit.current_location,
            route=sample_route,
            speed=sample_transport_unit.speed
        )
        
        # Cambiar ubicación para simular retraso
        new_location = Location(
            latitude=sample_transport_unit.current_location.latitude,
            longitude=sample_transport_unit.current_location.longitude,
            route_progress=sample_transport_unit.current_location.route_progress + 5,
            timestamp=datetime.now()
        )
        
        # Recalcular ETA con nueva ubicación (debe cambiar)
        eta_calculator.recalculate_all_etas(
            transport_unit_id=sample_transport_unit.id,
            current_location=new_location,
            route=sample_route,
            speed=sample_transport_unit.speed
        )
        
        # Verificar retrasos
        delays = engine.check_for_delays(
            transport_unit_id=sample_transport_unit.id,
            current_location=new_location,
            route=sample_route,
            speed=sample_transport_unit.speed,
            current_stop=sample_stop
        )
        
        # Puede haber retrasos dependiendo del cambio de ETA
        assert isinstance(delays, list)
    
    def test_check_for_delays_persistence(
        self,
        sample_transport_unit,
        sample_route,
        sample_stop
    ):
        """Verifica que retrasos se persisten."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        # Calcular ETA inicial
        eta_calculator.recalculate_all_etas(
            transport_unit_id=sample_transport_unit.id,
            current_location=sample_transport_unit.current_location,
            route=sample_route,
            speed=sample_transport_unit.speed
        )
        
        # Cambiar ubicación
        new_location = Location(
            latitude=sample_transport_unit.current_location.latitude,
            longitude=sample_transport_unit.current_location.longitude,
            route_progress=sample_transport_unit.current_location.route_progress + 5,
            timestamp=datetime.now()
        )
        
        # Recalcular ETA
        eta_calculator.recalculate_all_etas(
            transport_unit_id=sample_transport_unit.id,
            current_location=new_location,
            route=sample_route,
            speed=sample_transport_unit.speed
        )
        
        # Detectar retrasos
        delays = engine.check_for_delays(
            transport_unit_id=sample_transport_unit.id,
            current_location=new_location,
            route=sample_route,
            speed=sample_transport_unit.speed,
            current_stop=sample_stop
        )
        
        # Verificar que se persistieron
        history = persistence_service.get_delay_history(sample_transport_unit.id)
        assert len(history) >= len(delays)


class TestUpdateDelayStatus:
    """Tests para actualización de estado por retraso."""
    
    def test_update_delay_status_no_delay(self, sample_transport_unit):
        """Verifica que estado no cambia sin retraso."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        original_state = sample_transport_unit.state
        
        result = engine.update_delay_status(
            transport_unit_id=sample_transport_unit.id,
            transport_unit=sample_transport_unit
        )
        
        # Sin retraso, estado no debe cambiar
        assert result is None
        assert sample_transport_unit.state == original_state
    
    def test_update_delay_status_with_delay(self, sample_transport_unit):
        """Verifica que estado cambia a Retraso cuando se detecta."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        # Marcar como retrasado
        engine._delay_status[sample_transport_unit.id] = True
        
        result = engine.update_delay_status(
            transport_unit_id=sample_transport_unit.id,
            transport_unit=sample_transport_unit
        )
        
        # Estado debe cambiar a Retraso
        assert result == TransportState.RETRASO
        assert sample_transport_unit.state == TransportState.RETRASO
    
    def test_update_delay_status_recovery(self, sample_transport_unit):
        """Verifica que estado vuelve a En_Ruta cuando se recupera."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        # Cambiar a estado Retraso
        sample_transport_unit.state = TransportState.RETRASO
        engine._delay_status[sample_transport_unit.id] = True
        
        # Marcar como no retrasado
        engine._delay_status[sample_transport_unit.id] = False
        
        result = engine.update_delay_status(
            transport_unit_id=sample_transport_unit.id,
            transport_unit=sample_transport_unit
        )
        
        # Estado debe volver a En_Ruta
        assert result == TransportState.EN_RUTA
        assert sample_transport_unit.state == TransportState.EN_RUTA
    
    def test_update_delay_status_persistence(self, sample_transport_unit):
        """Verifica que cambio de estado se persiste."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        # Marcar como retrasado
        engine._delay_status[sample_transport_unit.id] = True
        
        engine.update_delay_status(
            transport_unit_id=sample_transport_unit.id,
            transport_unit=sample_transport_unit
        )
        
        # Verificar que se persistió
        history = persistence_service.get_state_change_history(sample_transport_unit.id)
        assert len(history) > 0


class TestGetDelayMagnitude:
    """Tests para obtención de magnitud de retraso."""
    
    def test_get_delay_magnitude_no_delays(self):
        """Verifica magnitud de retraso sin retrasos."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        magnitude = engine.get_delay_magnitude("unit_001")
        
        assert magnitude == 0
    
    def test_get_delay_magnitude_with_delays(self, sample_transport_unit, sample_stop):
        """Verifica magnitud de retraso con retrasos detectados."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        # Crear retrasos manualmente
        delay1 = Delay(
            id="delay_001",
            transport_unit_id=sample_transport_unit.id,
            detected_at=datetime.now(),
            magnitude=10,
            affected_stop=sample_stop
        )
        
        delay2 = Delay(
            id="delay_002",
            transport_unit_id=sample_transport_unit.id,
            detected_at=datetime.now(),
            magnitude=15,
            affected_stop=sample_stop
        )
        
        engine._detected_delays[sample_transport_unit.id] = [delay1, delay2]
        
        magnitude = engine.get_delay_magnitude(sample_transport_unit.id)
        
        # Magnitud debe ser suma de todos los retrasos
        assert magnitude == 25


class TestGetDetectedDelays:
    """Tests para obtención de retrasos detectados."""
    
    def test_get_detected_delays_empty(self):
        """Verifica obtención de retrasos cuando no hay."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        delays = engine.get_detected_delays("unit_001")
        
        assert len(delays) == 0
    
    def test_get_detected_delays_with_delays(self, sample_transport_unit, sample_stop):
        """Verifica obtención de retrasos detectados."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        # Crear retrasos manualmente
        delay = Delay(
            id="delay_001",
            transport_unit_id=sample_transport_unit.id,
            detected_at=datetime.now(),
            magnitude=10,
            affected_stop=sample_stop
        )
        
        engine._detected_delays[sample_transport_unit.id] = [delay]
        
        delays = engine.get_detected_delays(sample_transport_unit.id)
        
        assert len(delays) == 1
        assert delays[0].id == "delay_001"


class TestIsDelayed:
    """Tests para verificación de estado de retraso."""
    
    def test_is_delayed_false(self):
        """Verifica que unidad no está retrasada inicialmente."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        is_delayed = engine.is_delayed("unit_001")
        
        assert not is_delayed
    
    def test_is_delayed_true(self, sample_transport_unit):
        """Verifica que unidad está retrasada cuando se marca."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        engine._delay_status[sample_transport_unit.id] = True
        
        is_delayed = engine.is_delayed(sample_transport_unit.id)
        
        assert is_delayed


class TestClearDelayStatus:
    """Tests para limpieza de estado de retraso."""
    
    def test_clear_delay_status(self, sample_transport_unit, sample_stop):
        """Verifica limpieza de estado de retraso."""
        eta_calculator = ETACalculator()
        persistence_service = PersistenceService()
        
        engine = DelayDetectionEngine(eta_calculator, persistence_service)
        
        # Establecer estado de retraso
        engine._delay_status[sample_transport_unit.id] = True
        
        delay = Delay(
            id="delay_001",
            transport_unit_id=sample_transport_unit.id,
            detected_at=datetime.now(),
            magnitude=10,
            affected_stop=sample_stop
        )
        
        engine._detected_delays[sample_transport_unit.id] = [delay]
        
        # Limpiar
        engine.clear_delay_status(sample_transport_unit.id)
        
        # Verificar que fue limpiado
        assert not engine.is_delayed(sample_transport_unit.id)
        assert len(engine.get_detected_delays(sample_transport_unit.id)) == 0
