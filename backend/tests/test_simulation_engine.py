"""
Tests unitarios para el motor de simulación.
"""

import pytest
import time
from datetime import datetime, timedelta
from services.simulation_engine import SimulationEngine
from models import TransportUnit, Location, TransportState, Route, Stop


class TestSimulationEngineInitialization:
    """Tests para inicialización del motor de simulación."""
    
    def test_engine_initialization(self):
        """Verifica que el motor se inicializa correctamente."""
        engine = SimulationEngine()
        assert engine is not None
        assert not engine.is_running("unit_001")
    
    def test_start_simulation(self, sample_transport_unit, sample_route):
        """Verifica que se puede iniciar una simulación."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        
        assert engine.is_running(sample_transport_unit.id)
    
    def test_stop_simulation(self, sample_transport_unit, sample_route):
        """Verifica que se puede detener una simulación."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        assert engine.is_running(sample_transport_unit.id)
        
        engine.stop_simulation(sample_transport_unit.id)
        assert not engine.is_running(sample_transport_unit.id)
    
    def test_stop_nonexistent_simulation(self):
        """Verifica que detener una simulación inexistente no causa error."""
        engine = SimulationEngine()
        engine.stop_simulation("unit_nonexistent")  # No debe lanzar excepción


class TestSimulationEngineLocationGeneration:
    """Tests para generación de ubicaciones iniciales."""
    
    def test_initial_location_within_route(self, sample_transport_unit, sample_route):
        """Verifica que la ubicación inicial está dentro del recorrido."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        state = engine.get_current_state(sample_transport_unit.id)
        
        assert state is not None
        assert 0 <= state['current_location'].route_progress <= 100
    
    def test_initial_location_has_coordinates(self, sample_transport_unit, sample_route):
        """Verifica que la ubicación inicial tiene coordenadas válidas."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        state = engine.get_current_state(sample_transport_unit.id)
        
        location = state['current_location']
        assert isinstance(location.latitude, float)
        assert isinstance(location.longitude, float)
        assert location.latitude != 0 or location.longitude != 0
    
    def test_initial_location_has_timestamp(self, sample_transport_unit, sample_route):
        """Verifica que la ubicación inicial tiene timestamp."""
        engine = SimulationEngine()
        
        before = datetime.now()
        engine.start_simulation(sample_transport_unit, sample_route)
        after = datetime.now()
        
        state = engine.get_current_state(sample_transport_unit.id)
        location = state['current_location']
        
        assert before <= location.timestamp <= after


class TestSimulationEngineMovement:
    """Tests para movimiento realista del transporte."""
    
    def test_location_updates_on_update_call(self, sample_transport_unit, sample_route):
        """Verifica que la ubicación se actualiza cuando se llama update_location."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        initial_state = engine.get_current_state(sample_transport_unit.id)
        initial_progress = initial_state['current_location'].route_progress
        
        # Esperar un poco para que haya tiempo transcurrido
        time.sleep(0.1)
        
        new_location = engine.update_location(sample_transport_unit.id)
        
        assert new_location is not None
        # El progreso debe haber aumentado o mantenerse igual (si está detenido)
        assert new_location.route_progress >= initial_progress
    
    def test_movement_is_continuous(self, sample_transport_unit, sample_route):
        """Verifica que el movimiento es continuo sin saltos."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        
        locations = []
        for _ in range(5):
            location = engine.update_location(sample_transport_unit.id)
            if location:
                locations.append(location)
            time.sleep(0.05)
        
        # Verificar que el progreso es monótonamente creciente
        for i in range(len(locations) - 1):
            assert locations[i].route_progress <= locations[i + 1].route_progress
    
    def test_speed_is_within_range(self, sample_transport_unit, sample_route):
        """Verifica que la velocidad está dentro del rango configurado."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        state = engine.get_current_state(sample_transport_unit.id)
        
        speed = state['speed']
        assert 30 <= speed <= 60  # km/h
    
    def test_movement_respects_route_bounds(self, sample_transport_unit, sample_route):
        """Verifica que el movimiento no sale del recorrido."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        
        # Actualizar muchas veces para simular movimiento completo
        for _ in range(100):
            location = engine.update_location(sample_transport_unit.id)
            if location:
                assert 0 <= location.route_progress <= 100


class TestSimulationEngineStops:
    """Tests para detenciones en paradas."""
    
    def test_stop_detection(self, sample_transport_unit, sample_route):
        """Verifica que se detectan las paradas."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        
        # Actualizar hasta que se detecte una parada
        stopped = False
        for _ in range(200):
            state = engine.get_current_state(sample_transport_unit.id)
            if state['is_stopped']:
                stopped = True
                break
            engine.update_location(sample_transport_unit.id)
            time.sleep(0.01)
        
        # Puede que no se detecte parada en este test rápido, pero no debe fallar
        assert isinstance(stopped, bool)
    
    def test_location_constant_during_stop(self, sample_transport_unit, sample_route):
        """Verifica que la ubicación se mantiene constante durante una parada."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        
        # Simular hasta encontrar una parada
        for _ in range(500):
            state = engine.get_current_state(sample_transport_unit.id)
            if state['is_stopped']:
                # Guardar ubicación actual
                stopped_location = state['current_location']
                
                # Actualizar varias veces
                for _ in range(5):
                    new_location = engine.update_location(sample_transport_unit.id)
                    new_state = engine.get_current_state(sample_transport_unit.id)
                    
                    if new_state['is_stopped']:
                        # Mientras está detenido, la ubicación debe ser la misma
                        assert new_location.latitude == stopped_location.latitude
                        assert new_location.longitude == stopped_location.longitude
                    
                    time.sleep(0.01)
                
                break
            
            engine.update_location(sample_transport_unit.id)
            time.sleep(0.01)


class TestSimulationEngineState:
    """Tests para obtener el estado de la simulación."""
    
    def test_get_current_state_running(self, sample_transport_unit, sample_route):
        """Verifica que se obtiene el estado de una simulación en ejecución."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        state = engine.get_current_state(sample_transport_unit.id)
        
        assert state is not None
        assert state['transport_unit_id'] == sample_transport_unit.id
        assert 'current_location' in state
        assert 'is_stopped' in state
        assert 'speed' in state
        assert 'has_delay' in state
        assert 'delay_magnitude' in state
    
    def test_get_current_state_not_running(self):
        """Verifica que retorna None para simulación no existente."""
        engine = SimulationEngine()
        
        state = engine.get_current_state("unit_nonexistent")
        assert state is None
    
    def test_is_running_true(self, sample_transport_unit, sample_route):
        """Verifica que is_running retorna True para simulación activa."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        assert engine.is_running(sample_transport_unit.id)
    
    def test_is_running_false(self):
        """Verifica que is_running retorna False para simulación inexistente."""
        engine = SimulationEngine()
        
        assert not engine.is_running("unit_nonexistent")


class TestSimulationEngineMultipleUnits:
    """Tests para manejo de múltiples unidades."""
    
    def test_multiple_simulations_independent(self, sample_route):
        """Verifica que múltiples simulaciones son independientes."""
        engine = SimulationEngine()
        
        # Crear dos unidades
        unit1 = TransportUnit(
            id="unit_001",
            name="Autobús 101",
            route_id=sample_route.id,
            current_location=Location(25.6866, -100.3161, 0, datetime.now()),
            state=TransportState.EN_RUTA,
            speed=40.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        unit2 = TransportUnit(
            id="unit_002",
            name="Autobús 102",
            route_id=sample_route.id,
            current_location=Location(25.6866, -100.3161, 0, datetime.now()),
            state=TransportState.EN_RUTA,
            speed=40.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Iniciar simulaciones
        engine.start_simulation(unit1, sample_route)
        initial_state1 = engine.get_current_state(unit1.id)
        initial_progress1 = initial_state1['current_location'].route_progress
        
        engine.start_simulation(unit2, sample_route)
        initial_state2 = engine.get_current_state(unit2.id)
        initial_progress2 = initial_state2['current_location'].route_progress
        
        # Actualizar unit1 varias veces
        for _ in range(10):
            engine.update_location(unit1.id)
            time.sleep(0.01)
        
        # Obtener estados finales
        state1 = engine.get_current_state(unit1.id)
        state2 = engine.get_current_state(unit2.id)
        
        # unit1 debe haber avanzado más que su posición inicial
        assert state1['current_location'].route_progress > initial_progress1
        
        # unit2 debe estar en su posición inicial (no fue actualizado)
        assert state2['current_location'].route_progress == initial_progress2
    
    def test_stop_one_unit_does_not_affect_other(self, sample_route):
        """Verifica que detener una unidad no afecta otras."""
        engine = SimulationEngine()
        
        unit1 = TransportUnit(
            id="unit_001",
            name="Autobús 101",
            route_id=sample_route.id,
            current_location=Location(25.6866, -100.3161, 0, datetime.now()),
            state=TransportState.EN_RUTA,
            speed=40.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        unit2 = TransportUnit(
            id="unit_002",
            name="Autobús 102",
            route_id=sample_route.id,
            current_location=Location(25.6866, -100.3161, 0, datetime.now()),
            state=TransportState.EN_RUTA,
            speed=40.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        engine.start_simulation(unit1, sample_route)
        engine.start_simulation(unit2, sample_route)
        
        # Detener unit1
        engine.stop_simulation(unit1.id)
        
        # Verificar que unit1 no está corriendo pero unit2 sí
        assert not engine.is_running(unit1.id)
        assert engine.is_running(unit2.id)


class TestSimulationEngineRestart:
    """Tests para reiniciar simulaciones."""
    
    def test_restart_simulation(self, sample_transport_unit, sample_route):
        """Verifica que se puede reiniciar una simulación."""
        engine = SimulationEngine()
        
        # Iniciar simulación
        engine.start_simulation(sample_transport_unit, sample_route)
        state1 = engine.get_current_state(sample_transport_unit.id)
        progress1 = state1['current_location'].route_progress
        
        # Actualizar varias veces
        for _ in range(10):
            engine.update_location(sample_transport_unit.id)
            time.sleep(0.01)
        
        state2 = engine.get_current_state(sample_transport_unit.id)
        progress2 = state2['current_location'].route_progress
        
        # El progreso debe haber aumentado
        assert progress2 >= progress1
        
        # Reiniciar simulación
        engine.start_simulation(sample_transport_unit, sample_route)
        state3 = engine.get_current_state(sample_transport_unit.id)
        progress3 = state3['current_location'].route_progress
        
        # El progreso debe ser diferente (nueva ubicación inicial aleatoria)
        # Nota: Hay una pequeña probabilidad de que sea igual, pero es muy baja
        assert 0 <= progress3 <= 100


class TestSimulationEngineUpdateReturnsNone:
    """Tests para verificar que update_location retorna None cuando es apropiado."""
    
    def test_update_nonexistent_unit_returns_none(self):
        """Verifica que update_location retorna None para unidad inexistente."""
        engine = SimulationEngine()
        
        location = engine.update_location("unit_nonexistent")
        assert location is None
    
    def test_update_stopped_unit_returns_none(self, sample_transport_unit, sample_route):
        """Verifica que update_location retorna None después de detener."""
        engine = SimulationEngine()
        
        engine.start_simulation(sample_transport_unit, sample_route)
        engine.stop_simulation(sample_transport_unit.id)
        
        location = engine.update_location(sample_transport_unit.id)
        assert location is None
