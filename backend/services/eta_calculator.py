"""
Servicio de calculadora de tiempos estimados de llegada (ETA).

Este servicio proporciona:
- Cálculo de distancia entre ubicación actual y parada destino
- Estimación de tiempo basado en velocidad promedio
- Consideración de detenciones en paradas intermedias
- Recálculo automático de ETA cuando cambia la ubicación
"""

import math
from typing import Dict, List, Optional, Tuple
from models import Location, Route, Stop, TransportUnit


class ETACalculator:
    """
    Calculadora de tiempos estimados de llegada (ETA).
    
    Calcula:
    - Distancia entre ubicación actual y parada destino
    - Tiempo estimado basado en velocidad promedio
    - Consideración de detenciones en paradas intermedias
    - Recálculo automático de ETA
    """
    
    # Constante de la Tierra en km para cálculo de distancia
    EARTH_RADIUS_KM = 6371.0
    
    def __init__(self):
        """Inicializa la calculadora de ETA."""
        # Caché de ETAs: {transport_unit_id: {stop_id: eta_minutes}}
        self._eta_cache: Dict[str, Dict[str, float]] = {}
    
    def calculate_eta(
        self,
        current_location: Location,
        target_stop: Stop,
        speed: float,
        intermediate_stops: Optional[List[Stop]] = None
    ) -> float:
        """
        Calcula el tiempo estimado de llegada a una parada.
        
        Args:
            current_location: Ubicación actual de la unidad
            target_stop: Parada destino
            speed: Velocidad promedio en km/h
            intermediate_stops: Paradas intermedias donde se detendrá (opcional)
            
        Returns:
            Tiempo estimado en minutos (redondeado a entero)
        """
        if speed <= 0:
            return 0
        
        # Calcular distancia desde ubicación actual a parada destino
        distance_km = self._calculate_distance(
            current_location.latitude,
            current_location.longitude,
            target_stop.latitude,
            target_stop.longitude
        )
        
        # Calcular tiempo de viaje en minutos
        travel_time_minutes = (distance_km / speed) * 60
        
        # Calcular tiempo de detenciones en paradas intermedias
        stop_time_minutes = 0
        if intermediate_stops:
            for stop in intermediate_stops:
                # Convertir duración de segundos a minutos
                stop_time_minutes += stop.estimated_stop_duration / 60
        
        # ETA total = tiempo de viaje + tiempo de detenciones
        total_eta = travel_time_minutes + stop_time_minutes
        
        return round(total_eta)
    
    def recalculate_all_etas(
        self,
        transport_unit_id: str,
        current_location: Location,
        route: Route,
        speed: float
    ) -> Dict[str, float]:
        """
        Recalcula el ETA para todas las paradas del recorrido.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            current_location: Ubicación actual
            route: Recorrido completo
            speed: Velocidad promedio en km/h
            
        Returns:
            Diccionario con {stop_id: eta_minutes} para todas las paradas
        """
        etas = {}
        
        # Encontrar índice de la parada actual basado en route_progress
        current_stop_index = self._find_current_stop_index(current_location, route)
        
        # Calcular ETA para cada parada desde la actual en adelante
        for i, stop in enumerate(route.stops):
            if i >= current_stop_index:
                # Paradas intermedias entre ubicación actual y parada destino
                intermediate_stops = route.stops[current_stop_index:i]
                
                eta = self.calculate_eta(
                    current_location,
                    stop,
                    speed,
                    intermediate_stops
                )
                etas[stop.id] = eta
        
        # Guardar en caché
        if transport_unit_id not in self._eta_cache:
            self._eta_cache[transport_unit_id] = {}
        self._eta_cache[transport_unit_id].update(etas)
        
        return etas
    
    def estimate_delay_at_stop(self, stop: Stop) -> float:
        """
        Estima el retraso potencial en una parada.
        
        Args:
            stop: Parada donde se estima el retraso
            
        Returns:
            Duración estimada de la detención en minutos
        """
        # Convertir duración de segundos a minutos
        return stop.estimated_stop_duration / 60
    
    def get_cached_eta(self, transport_unit_id: str, stop_id: str) -> Optional[float]:
        """
        Obtiene el ETA en caché para una parada específica.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            stop_id: ID de la parada
            
        Returns:
            ETA en minutos o None si no está en caché
        """
        if transport_unit_id in self._eta_cache:
            return self._eta_cache[transport_unit_id].get(stop_id)
        return None
    
    def clear_cache(self, transport_unit_id: str) -> None:
        """
        Limpia el caché de ETA para una unidad.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
        """
        if transport_unit_id in self._eta_cache:
            del self._eta_cache[transport_unit_id]
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calcula la distancia entre dos puntos usando la fórmula de Haversine.
        
        Args:
            lat1: Latitud del punto 1
            lon1: Longitud del punto 1
            lat2: Latitud del punto 2
            lon2: Longitud del punto 2
            
        Returns:
            Distancia en kilómetros
        """
        # Convertir grados a radianes
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Diferencias
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Fórmula de Haversine
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        # Distancia en km
        distance = self.EARTH_RADIUS_KM * c
        
        return distance
    
    def _find_current_stop_index(self, location: Location, route: Route) -> int:
        """
        Encuentra el índice de la parada actual basado en route_progress.
        
        Args:
            location: Ubicación actual
            route: Recorrido
            
        Returns:
            Índice de la parada actual (0 si está antes de la primera parada)
        """
        # route_progress es un porcentaje (0-100)
        # Convertir a índice de parada
        if location.route_progress <= 0:
            return 0
        
        if location.route_progress >= 100:
            return len(route.stops) - 1
        
        # Calcular índice basado en porcentaje
        stop_index = int((location.route_progress / 100) * len(route.stops))
        
        # Asegurar que está dentro de rango
        return min(stop_index, len(route.stops) - 1)
