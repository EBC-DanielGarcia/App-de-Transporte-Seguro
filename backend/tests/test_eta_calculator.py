"""
Tests unitarios para la calculadora de ETA.
"""

import pytest
import math
from datetime import datetime
from services.eta_calculator import ETACalculator
from models import Location, Route, Stop, TransportUnit, TransportState


class TestETACalculatorInitialization:
    """Tests para inicialización de la calculadora de ETA."""
    
    def test_calculator_initialization(self):
        """Verifica que la calculadora se inicializa correctamente."""
        calculator = ETACalculator()
        assert calculator is not None
        assert calculator.EARTH_RADIUS_KM == 6371.0


class TestETACalculation:
    """Tests para cálculo de ETA."""
    
    def test_calculate_eta_basic(self, sample_location, sample_stop):
        """Verifica cálculo básico de ETA."""
        calculator = ETACalculator()
        
        # Ubicación actual y parada destino
        eta = calculator.calculate_eta(
            current_location=sample_location,
            target_stop=sample_stop,
            speed=40.0  # 40 km/h
        )
        
        # ETA debe ser un número positivo
        assert isinstance(eta, int)
        assert eta >= 0
    
    def test_calculate_eta_with_zero_speed(self, sample_location, sample_stop):
        """Verifica que ETA es 0 con velocidad 0."""
        calculator = ETACalculator()
        
        eta = calculator.calculate_eta(
            current_location=sample_location,
            target_stop=sample_stop,
            speed=0.0
        )
        
        assert eta == 0
    
    def test_calculate_eta_with_intermediate_stops(self, sample_location, sample_stops):
        """Verifica cálculo de ETA considerando paradas intermedias."""
        calculator = ETACalculator()
        
        # Parada destino es la última
        target_stop = sample_stops[-1]
        
        # Paradas intermedias
        intermediate_stops = sample_stops[:-1]
        
        eta_without_stops = calculator.calculate_eta(
            current_location=sample_location,
            target_stop=target_stop,
            speed=40.0
        )
        
        eta_with_stops = calculator.calculate_eta(
            current_location=sample_location,
            target_stop=target_stop,
            speed=40.0,
            intermediate_stops=intermediate_stops
        )
        
        # ETA con paradas debe ser mayor
        assert eta_with_stops >= eta_without_stops
    
    def test_calculate_eta_same_location(self, sample_location):
        """Verifica ETA cuando ubicación actual es igual a parada destino."""
        calculator = ETACalculator()
        
        # Crear parada en la misma ubicación
        same_stop = Stop(
            id="stop_same",
            name="Misma Ubicación",
            latitude=sample_location.latitude,
            longitude=sample_location.longitude,
            distance_from_start=0.0,
            estimated_stop_duration=60
        )
        
        eta = calculator.calculate_eta(
            current_location=sample_location,
            target_stop=same_stop,
            speed=40.0
        )
        
        # ETA debe ser muy pequeño (cercano a 0)
        assert eta == 0
    
    def test_calculate_eta_different_speeds(self, sample_location, sample_stop):
        """Verifica que ETA disminuye con mayor velocidad."""
        calculator = ETACalculator()
        
        eta_slow = calculator.calculate_eta(
            current_location=sample_location,
            target_stop=sample_stop,
            speed=20.0  # 20 km/h
        )
        
        eta_fast = calculator.calculate_eta(
            current_location=sample_location,
            target_stop=sample_stop,
            speed=60.0  # 60 km/h
        )
        
        # ETA con velocidad mayor debe ser menor
        assert eta_fast <= eta_slow


class TestRecalculateAllETAs:
    """Tests para recálculo de ETA para todas las paradas."""
    
    def test_recalculate_all_etas(self, sample_transport_unit, sample_route):
        """Verifica recálculo de ETA para todas las paradas."""
        calculator = ETACalculator()
        
        etas = calculator.recalculate_all_etas(
            transport_unit_id=sample_transport_unit.id,
            current_location=sample_transport_unit.current_location,
            route=sample_route,
            speed=sample_transport_unit.speed
        )
        
        # Debe haber ETA para cada parada
        assert len(etas) > 0
        
        # Todos los valores deben ser números positivos
        for stop_id, eta in etas.items():
            assert isinstance(eta, (int, float))
            assert eta >= 0
    
    def test_recalculate_all_etas_caching(self, sample_transport_unit, sample_route):
        """Verifica que ETAs se cachean correctamente."""
        calculator = ETACalculator()
        
        etas1 = calculator.recalculate_all_etas(
            transport_unit_id=sample_transport_unit.id,
            current_location=sample_transport_unit.current_location,
            route=sample_route,
            speed=sample_transport_unit.speed
        )
        
        # Obtener del caché - usar una parada que esté en el caché
        if len(etas1) > 0:
            first_cached_stop_id = list(etas1.keys())[0]
            cached_eta = calculator.get_cached_eta(
                sample_transport_unit.id,
                first_cached_stop_id
            )
            
            assert cached_eta is not None
            assert cached_eta == etas1[first_cached_stop_id]
    
    def test_recalculate_all_etas_increasing_order(self, sample_transport_unit, sample_route):
        """Verifica que ETAs aumentan para paradas más lejanas."""
        calculator = ETACalculator()
        
        etas = calculator.recalculate_all_etas(
            transport_unit_id=sample_transport_unit.id,
            current_location=sample_transport_unit.current_location,
            route=sample_route,
            speed=sample_transport_unit.speed
        )
        
        # Convertir a lista ordenada por índice de parada
        eta_values = [etas[stop.id] for stop in sample_route.stops if stop.id in etas]
        
        # ETAs deben ser no decrecientes (aumentan o se mantienen)
        for i in range(len(eta_values) - 1):
            assert eta_values[i] <= eta_values[i + 1]


class TestEstimateDelayAtStop:
    """Tests para estimación de retraso en parada."""
    
    def test_estimate_delay_at_stop(self, sample_stop):
        """Verifica estimación de retraso en parada."""
        calculator = ETACalculator()
        
        delay = calculator.estimate_delay_at_stop(sample_stop)
        
        # Debe ser un número positivo
        assert isinstance(delay, float)
        assert delay > 0
        
        # Debe ser la duración estimada en minutos
        expected_delay = sample_stop.estimated_stop_duration / 60
        assert delay == expected_delay
    
    def test_estimate_delay_at_stop_zero_duration(self):
        """Verifica estimación de retraso con duración 0."""
        calculator = ETACalculator()
        
        stop = Stop(
            id="stop_zero",
            name="Parada Sin Duración",
            latitude=25.6866,
            longitude=-100.3161,
            distance_from_start=0.0,
            estimated_stop_duration=0
        )
        
        delay = calculator.estimate_delay_at_stop(stop)
        
        assert delay == 0.0


class TestCacheManagement:
    """Tests para gestión de caché de ETA."""
    
    def test_get_cached_eta_nonexistent(self):
        """Verifica que obtener ETA no existente retorna None."""
        calculator = ETACalculator()
        
        cached_eta = calculator.get_cached_eta("unit_nonexistent", "stop_nonexistent")
        
        assert cached_eta is None
    
    def test_clear_cache(self, sample_transport_unit, sample_route):
        """Verifica limpieza de caché."""
        calculator = ETACalculator()
        
        # Calcular y cachear ETAs
        etas = calculator.recalculate_all_etas(
            transport_unit_id=sample_transport_unit.id,
            current_location=sample_transport_unit.current_location,
            route=sample_route,
            speed=sample_transport_unit.speed
        )
        
        # Verificar que está en caché - usar una parada que esté en el caché
        if len(etas) > 0:
            first_cached_stop_id = list(etas.keys())[0]
            cached_eta = calculator.get_cached_eta(
                sample_transport_unit.id,
                first_cached_stop_id
            )
            assert cached_eta is not None
            
            # Limpiar caché
            calculator.clear_cache(sample_transport_unit.id)
            
            # Verificar que fue limpiado
            cached_eta = calculator.get_cached_eta(
                sample_transport_unit.id,
                first_cached_stop_id
            )
            assert cached_eta is None


class TestDistanceCalculation:
    """Tests para cálculo de distancia (Haversine)."""
    
    def test_distance_same_point(self):
        """Verifica distancia entre el mismo punto."""
        calculator = ETACalculator()
        
        distance = calculator._calculate_distance(
            lat1=25.6866,
            lon1=-100.3161,
            lat2=25.6866,
            lon2=-100.3161
        )
        
        # Distancia debe ser 0
        assert distance == 0.0
    
    def test_distance_different_points(self):
        """Verifica distancia entre puntos diferentes."""
        calculator = ETACalculator()
        
        # Monterrey a Guadalajara (aproximadamente 640 km)
        distance = calculator._calculate_distance(
            lat1=25.6866,
            lon1=-100.3161,
            lat2=20.6597,
            lon2=-103.3496
        )
        
        # Distancia debe ser positiva y razonable
        assert distance > 0
        assert 600 < distance < 700  # Aproximadamente 640 km
    
    def test_distance_symmetry(self):
        """Verifica que la distancia es simétrica."""
        calculator = ETACalculator()
        
        distance1 = calculator._calculate_distance(
            lat1=25.6866,
            lon1=-100.3161,
            lat2=20.6597,
            lon2=-103.3496
        )
        
        distance2 = calculator._calculate_distance(
            lat1=20.6597,
            lon1=-103.3496,
            lat2=25.6866,
            lon2=-100.3161
        )
        
        # Distancias deben ser iguales
        assert abs(distance1 - distance2) < 0.01


class TestFindCurrentStopIndex:
    """Tests para búsqueda de índice de parada actual."""
    
    def test_find_current_stop_index_start(self, sample_route):
        """Verifica búsqueda de índice al inicio del recorrido."""
        calculator = ETACalculator()
        
        location = Location(
            latitude=25.6866,
            longitude=-100.3161,
            route_progress=0.0,
            timestamp=datetime.now()
        )
        
        index = calculator._find_current_stop_index(location, sample_route)
        
        assert index == 0
    
    def test_find_current_stop_index_middle(self, sample_route):
        """Verifica búsqueda de índice en medio del recorrido."""
        calculator = ETACalculator()
        
        location = Location(
            latitude=25.6866,
            longitude=-100.3161,
            route_progress=50.0,
            timestamp=datetime.now()
        )
        
        index = calculator._find_current_stop_index(location, sample_route)
        
        # Debe estar entre 0 y número de paradas
        assert 0 <= index < len(sample_route.stops)
    
    def test_find_current_stop_index_end(self, sample_route):
        """Verifica búsqueda de índice al final del recorrido."""
        calculator = ETACalculator()
        
        location = Location(
            latitude=25.6866,
            longitude=-100.3161,
            route_progress=100.0,
            timestamp=datetime.now()
        )
        
        index = calculator._find_current_stop_index(location, sample_route)
        
        assert index == len(sample_route.stops) - 1
