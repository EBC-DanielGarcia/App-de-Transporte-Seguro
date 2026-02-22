"""
Tests unitarios para el scheduler de simulación.
"""

import pytest
import time
from datetime import datetime
from services.simulation_scheduler import SimulationScheduler
from services.simulation_engine import SimulationEngine
from models import TransportUnit, Location, TransportState


class TestSimulationSchedulerInitialization:
    """Tests para inicialización del scheduler."""
    
    def test_scheduler_initialization(self):
        """Verifica que el scheduler se inicializa correctamente."""
        scheduler = SimulationScheduler()
        assert scheduler is not None
        assert not scheduler.is_scheduler_running()
    
    def test_scheduler_with_custom_engine(self):
        """Verifica que se puede proporcionar un motor personalizado."""
        engine = SimulationEngine()
        scheduler = SimulationScheduler(simulation_engine=engine)
        assert scheduler is not None
    
    def test_scheduler_with_custom_interval(self):
        """Verifica que se puede configurar intervalo personalizado."""
        scheduler = SimulationScheduler(update_interval=0.5)
        assert scheduler is not None


class TestSimulationSchedulerStartStop:
    """Tests para iniciar y detener el scheduler."""
    
    def test_start_scheduler(self):
        """Verifica que se puede iniciar el scheduler."""
        scheduler = SimulationScheduler()
        
        scheduler.start_scheduler()
        assert scheduler.is_scheduler_running()
        
        scheduler.stop_scheduler()
    
    def test_stop_scheduler(self):
        """Verifica que se puede detener el scheduler."""
        scheduler = SimulationScheduler()
        
        scheduler.start_scheduler()
        assert scheduler.is_scheduler_running()
        
        scheduler.stop_scheduler()
        assert not scheduler.is_scheduler_running()
    
    def test_start_already_running_scheduler(self):
        """Verifica que iniciar un scheduler ya corriendo no causa error."""
        scheduler = SimulationScheduler()
        
        scheduler.start_scheduler()
        scheduler.start_scheduler()  # No debe causar error
        
        assert scheduler.is_scheduler_running()
        scheduler.stop_scheduler()
    
    def test_stop_already_stopped_scheduler(self):
        """Verifica que detener un scheduler ya detenido no causa error."""
        scheduler = SimulationScheduler()
        
        scheduler.stop_scheduler()  # No debe causar error
        assert not scheduler.is_scheduler_running()


class TestSimulationSchedulerTransportUnits:
    """Tests para agregar y remover unidades de transporte."""
    
    def test_add_transport_unit(self, sample_transport_unit, sample_route):
        """Verifica que se puede agregar una unidad de transporte."""
        scheduler = SimulationScheduler()
        
        scheduler.add_transport_unit(sample_transport_unit, sample_route)
        
        active_units = scheduler.get_active_units()
        assert sample_transport_unit.id in active_units
    
    def test_remove_transport_unit(self, sample_transport_unit, sample_route):
        """Verifica que se puede remover una unidad de transporte."""
        scheduler = SimulationScheduler()
        
        scheduler.add_transport_unit(sample_transport_unit, sample_route)
        assert sample_transport_unit.id in scheduler.get_active_units()
        
        scheduler.remove_transport_unit(sample_transport_unit.id)
        assert sample_transport_unit.id not in scheduler.get_active_units()
    
    def test_remove_nonexistent_unit(self):
        """Verifica que remover una unidad inexistente no causa error."""
        scheduler = SimulationScheduler()
        
        scheduler.remove_transport_unit("unit_nonexistent")  # No debe causar error
    
    def test_get_active_units_empty(self):
        """Verifica que get_active_units retorna lista vacía inicialmente."""
        scheduler = SimulationScheduler()
        
        active_units = scheduler.get_active_units()
        assert active_units == []
    
    def test_get_active_units_multiple(self, sample_route):
        """Verifica que get_active_units retorna todas las unidades."""
        scheduler = SimulationScheduler()
        
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
        
        scheduler.add_transport_unit(unit1, sample_route)
        scheduler.add_transport_unit(unit2, sample_route)
        
        active_units = scheduler.get_active_units()
        assert len(active_units) == 2
        assert "unit_001" in active_units
        assert "unit_002" in active_units


class TestSimulationSchedulerCallbacks:
    """Tests para callbacks de actualización."""
    
    def test_register_callback(self):
        """Verifica que se puede registrar un callback."""
        scheduler = SimulationScheduler()
        
        def dummy_callback(unit_id, location):
            pass
        
        scheduler.register_update_callback(dummy_callback)
        # No debe causar error
    
    def test_unregister_callback(self):
        """Verifica que se puede desregistrar un callback."""
        scheduler = SimulationScheduler()
        
        def dummy_callback(unit_id, location):
            pass
        
        scheduler.register_update_callback(dummy_callback)
        scheduler.unregister_update_callback(dummy_callback)
        # No debe causar error
    
    def test_callback_called_on_update(self, sample_transport_unit, sample_route):
        """Verifica que los callbacks se llaman cuando se actualiza."""
        scheduler = SimulationScheduler()
        
        # Crear lista para rastrear llamadas
        updates = []
        
        def track_updates(unit_id, location):
            updates.append((unit_id, location))
        
        scheduler.register_update_callback(track_updates)
        scheduler.add_transport_unit(sample_transport_unit, sample_route)
        
        # Iniciar scheduler
        scheduler.start_scheduler()
        
        # Esperar a que se realicen actualizaciones
        time.sleep(2.5)
        
        scheduler.stop_scheduler()
        
        # Debe haber al menos 2 actualizaciones (cada segundo)
        assert len(updates) >= 2
        
        # Verificar que los updates tienen el formato correcto
        for unit_id, location in updates:
            assert unit_id == sample_transport_unit.id
            assert location is not None
            assert hasattr(location, 'latitude')
            assert hasattr(location, 'longitude')
    
    def test_multiple_callbacks(self, sample_transport_unit, sample_route):
        """Verifica que múltiples callbacks se llaman."""
        scheduler = SimulationScheduler()
        
        updates1 = []
        updates2 = []
        
        def callback1(unit_id, location):
            updates1.append((unit_id, location))
        
        def callback2(unit_id, location):
            updates2.append((unit_id, location))
        
        scheduler.register_update_callback(callback1)
        scheduler.register_update_callback(callback2)
        scheduler.add_transport_unit(sample_transport_unit, sample_route)
        
        scheduler.start_scheduler()
        time.sleep(1.5)
        scheduler.stop_scheduler()
        
        # Ambos callbacks deben haber sido llamados
        assert len(updates1) >= 1
        assert len(updates2) >= 1


class TestSimulationSchedulerPeriodicUpdates:
    """Tests para verificar que las actualizaciones son periódicas."""
    
    def test_updates_at_regular_intervals(self, sample_transport_unit, sample_route):
        """Verifica que las actualizaciones ocurren a intervalos regulares."""
        scheduler = SimulationScheduler(update_interval=0.5)
        
        update_times = []
        
        def track_time(unit_id, location):
            update_times.append(datetime.now())
        
        scheduler.register_update_callback(track_time)
        scheduler.add_transport_unit(sample_transport_unit, sample_route)
        
        scheduler.start_scheduler()
        time.sleep(2.0)
        scheduler.stop_scheduler()
        
        # Debe haber aproximadamente 4 actualizaciones (cada 0.5 segundos)
        assert len(update_times) >= 3
        
        # Verificar que los intervalos son aproximadamente regulares
        if len(update_times) >= 2:
            intervals = []
            for i in range(1, len(update_times)):
                interval = (update_times[i] - update_times[i-1]).total_seconds()
                intervals.append(interval)
            
            # Los intervalos deben estar cerca de 0.5 segundos
            avg_interval = sum(intervals) / len(intervals)
            assert 0.3 <= avg_interval <= 0.7  # Permitir cierta variación
    
    def test_no_gaps_in_updates(self, sample_transport_unit, sample_route):
        """Verifica que no hay gaps en las actualizaciones."""
        scheduler = SimulationScheduler(update_interval=0.2)
        
        update_count = [0]
        
        def count_updates(unit_id, location):
            update_count[0] += 1
        
        scheduler.register_update_callback(count_updates)
        scheduler.add_transport_unit(sample_transport_unit, sample_route)
        
        scheduler.start_scheduler()
        time.sleep(1.0)
        scheduler.stop_scheduler()
        
        # Debe haber aproximadamente 5 actualizaciones (cada 0.2 segundos)
        assert update_count[0] >= 4


class TestSimulationSchedulerMultipleUnits:
    """Tests para manejo de múltiples unidades."""
    
    def test_updates_multiple_units(self, sample_route):
        """Verifica que se actualizan múltiples unidades."""
        scheduler = SimulationScheduler()
        
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
        
        updates_by_unit = {}
        
        def track_updates(unit_id, location):
            if unit_id not in updates_by_unit:
                updates_by_unit[unit_id] = []
            updates_by_unit[unit_id].append(location)
        
        scheduler.register_update_callback(track_updates)
        scheduler.add_transport_unit(unit1, sample_route)
        scheduler.add_transport_unit(unit2, sample_route)
        
        scheduler.start_scheduler()
        time.sleep(1.5)
        scheduler.stop_scheduler()
        
        # Ambas unidades deben haber sido actualizadas
        assert "unit_001" in updates_by_unit
        assert "unit_002" in updates_by_unit
        assert len(updates_by_unit["unit_001"]) >= 1
        assert len(updates_by_unit["unit_002"]) >= 1
    
    def test_remove_unit_stops_updates(self, sample_route):
        """Verifica que remover una unidad detiene sus actualizaciones."""
        scheduler = SimulationScheduler()
        
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
        
        updates_by_unit = {}
        
        def track_updates(unit_id, location):
            if unit_id not in updates_by_unit:
                updates_by_unit[unit_id] = []
            updates_by_unit[unit_id].append(location)
        
        scheduler.register_update_callback(track_updates)
        scheduler.add_transport_unit(unit1, sample_route)
        scheduler.add_transport_unit(unit2, sample_route)
        
        scheduler.start_scheduler()
        time.sleep(0.5)
        
        # Remover unit1
        scheduler.remove_transport_unit("unit_001")
        
        time.sleep(1.0)
        scheduler.stop_scheduler()
        
        # unit1 debe tener pocas actualizaciones, unit2 debe tener más
        unit1_updates = len(updates_by_unit.get("unit_001", []))
        unit2_updates = len(updates_by_unit.get("unit_002", []))
        
        assert unit1_updates < unit2_updates


class TestSimulationSchedulerThreadSafety:
    """Tests para verificar thread-safety del scheduler."""
    
    def test_add_unit_while_running(self, sample_route):
        """Verifica que se puede agregar una unidad mientras el scheduler corre."""
        scheduler = SimulationScheduler()
        
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
        
        scheduler.add_transport_unit(unit1, sample_route)
        scheduler.start_scheduler()
        
        time.sleep(0.5)
        
        # Agregar unit2 mientras el scheduler corre
        scheduler.add_transport_unit(unit2, sample_route)
        
        time.sleep(0.5)
        scheduler.stop_scheduler()
        
        # Ambas unidades deben estar en la lista
        active_units = scheduler.get_active_units()
        assert "unit_001" in active_units
        assert "unit_002" in active_units
    
    def test_remove_unit_while_running(self, sample_route):
        """Verifica que se puede remover una unidad mientras el scheduler corre."""
        scheduler = SimulationScheduler()
        
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
        
        scheduler.add_transport_unit(unit1, sample_route)
        scheduler.start_scheduler()
        
        time.sleep(0.5)
        
        # Remover unit1 mientras el scheduler corre
        scheduler.remove_transport_unit("unit_001")
        
        time.sleep(0.5)
        scheduler.stop_scheduler()
        
        # unit1 no debe estar en la lista
        active_units = scheduler.get_active_units()
        assert "unit_001" not in active_units
