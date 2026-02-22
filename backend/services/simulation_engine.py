"""
Motor de simulación de movimiento de unidades de transporte.

Este servicio proporciona:
- Generación de ubicaciones iniciales aleatorias
- Movimiento realista a lo largo del recorrido
- Detenciones en paradas con duración variable
- Retrasos ocasionales
- Actualización periódica de ubicaciones
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from models import TransportUnit, Location, TransportState, Route
from models.stop import Stop


class SimulationEngine:
    """
    Motor de simulación para unidades de transporte.
    
    Genera y actualiza datos simulados de ubicación y estado del transporte.
    """
    
    def __init__(self):
        """Inicializa el motor de simulación."""
        # Almacenamiento de simulaciones activas: {transport_unit_id: simulation_state}
        self._active_simulations: Dict[str, Dict] = {}
        
        # Configuración de simulación
        self._min_speed = 30  # km/h
        self._max_speed = 60  # km/h
        self._min_stop_duration = 30  # segundos
        self._max_stop_duration = 120  # segundos
        self._delay_probability = 0.15  # 15% de probabilidad de retraso
        self._delay_min = 5  # minutos
        self._delay_max = 20  # minutos
    
    def start_simulation(self, transport_unit: TransportUnit, route: Route) -> None:
        """
        Inicia la simulación de una unidad de transporte.
        
        Args:
            transport_unit: Unidad de transporte a simular
            route: Recorrido que debe seguir la unidad
        """
        if transport_unit.id in self._active_simulations:
            # Si ya existe una simulación, detenerla primero
            self.stop_simulation(transport_unit.id)
        
        # Generar ubicación inicial aleatoria en el recorrido
        initial_location = self._generate_initial_location(route)
        
        # Crear estado de simulación
        simulation_state = {
            'transport_unit': transport_unit,
            'route': route,
            'current_location': initial_location,
            'current_stop_index': self._find_current_stop_index(initial_location, route),
            'is_stopped': False,
            'stop_end_time': None,
            'speed': random.uniform(self._min_speed, self._max_speed),
            'has_delay': random.random() < self._delay_probability,
            'delay_magnitude': random.randint(self._delay_min, self._delay_max) if random.random() < self._delay_probability else 0,
            'last_update': datetime.now(),
            'started_at': datetime.now(),
        }
        
        self._active_simulations[transport_unit.id] = simulation_state
    
    def stop_simulation(self, transport_unit_id: str) -> None:
        """
        Detiene la simulación de una unidad de transporte.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
        """
        if transport_unit_id in self._active_simulations:
            del self._active_simulations[transport_unit_id]
    
    def update_location(self, transport_unit_id: str) -> Optional[Location]:
        """
        Actualiza la ubicación de una unidad de transporte en simulación.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Nueva ubicación actualizada, o None si no está en simulación
        """
        if transport_unit_id not in self._active_simulations:
            return None
        
        simulation_state = self._active_simulations[transport_unit_id]
        route = simulation_state['route']
        current_location = simulation_state['current_location']
        
        # Calcular tiempo transcurrido desde la última actualización
        now = datetime.now()
        time_elapsed = (now - simulation_state['last_update']).total_seconds()
        
        # Si está detenido en una parada, verificar si debe continuar
        if simulation_state['is_stopped']:
            if now >= simulation_state['stop_end_time']:
                # Terminar la detención
                simulation_state['is_stopped'] = False
                simulation_state['stop_end_time'] = None
                simulation_state['current_stop_index'] += 1
            else:
                # Mantener la ubicación actual
                simulation_state['last_update'] = now
                return current_location
        
        # Calcular distancia a recorrer basada en velocidad y tiempo
        speed_km_per_second = simulation_state['speed'] / 3600  # Convertir km/h a km/s
        distance_to_travel = speed_km_per_second * time_elapsed
        
        # Actualizar progreso en el recorrido
        new_route_progress = current_location.route_progress + (distance_to_travel / route.total_distance) * 100
        
        # Verificar si llegó al final del recorrido
        if new_route_progress >= 100.0:
            new_route_progress = 100.0
        
        # Calcular nuevas coordenadas interpolando entre paradas
        new_latitude, new_longitude = self._interpolate_coordinates(
            current_location.latitude,
            current_location.longitude,
            route,
            new_route_progress
        )
        
        # Crear nueva ubicación
        new_location = Location(
            latitude=new_latitude,
            longitude=new_longitude,
            route_progress=new_route_progress,
            timestamp=now
        )
        
        # Verificar si llegó a una parada
        current_stop_index = self._find_current_stop_index(new_location, route)
        if current_stop_index != simulation_state['current_stop_index'] and current_stop_index < len(route.stops):
            # Llegó a una nueva parada, iniciar detención
            stop = route.stops[current_stop_index]
            stop_duration = random.randint(self._min_stop_duration, self._max_stop_duration)
            
            simulation_state['is_stopped'] = True
            simulation_state['stop_end_time'] = now + timedelta(seconds=stop_duration)
            simulation_state['current_stop_index'] = current_stop_index
        
        # Actualizar estado de simulación
        simulation_state['current_location'] = new_location
        simulation_state['last_update'] = now
        
        return new_location
    
    def get_current_state(self, transport_unit_id: str) -> Optional[Dict]:
        """
        Obtiene el estado actual de una unidad en simulación.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Diccionario con el estado actual, o None si no está en simulación
        """
        if transport_unit_id not in self._active_simulations:
            return None
        
        simulation_state = self._active_simulations[transport_unit_id]
        
        return {
            'transport_unit_id': transport_unit_id,
            'current_location': simulation_state['current_location'],
            'is_stopped': simulation_state['is_stopped'],
            'speed': simulation_state['speed'],
            'has_delay': simulation_state['has_delay'],
            'delay_magnitude': simulation_state['delay_magnitude'],
            'current_stop_index': simulation_state['current_stop_index'],
            'total_stops': len(simulation_state['route'].stops),
        }
    
    def is_running(self, transport_unit_id: str) -> bool:
        """
        Verifica si una unidad está en simulación.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            True si está en simulación, False en caso contrario
        """
        return transport_unit_id in self._active_simulations
    
    def _generate_initial_location(self, route: Route) -> Location:
        """
        Genera una ubicación inicial aleatoria en el recorrido.
        
        Args:
            route: Recorrido donde generar la ubicación
            
        Returns:
            Ubicación inicial aleatoria
        """
        # Generar progreso aleatorio entre 0 y 100
        route_progress = random.uniform(0, 100)
        
        # Interpolar coordenadas basadas en el progreso
        latitude, longitude = self._interpolate_coordinates(
            route.stops[0].latitude,
            route.stops[0].longitude,
            route,
            route_progress
        )
        
        return Location(
            latitude=latitude,
            longitude=longitude,
            route_progress=route_progress,
            timestamp=datetime.now()
        )
    
    def _interpolate_coordinates(
        self,
        current_lat: float,
        current_lon: float,
        route: Route,
        route_progress: float
    ) -> Tuple[float, float]:
        """
        Interpola coordenadas basadas en el progreso en el recorrido.
        
        Args:
            current_lat: Latitud actual
            current_lon: Longitud actual
            route: Recorrido
            route_progress: Progreso en el recorrido (0-100)
            
        Returns:
            Tupla (latitud, longitud) interpolada
        """
        if not route.stops or len(route.stops) < 2:
            return current_lat, current_lon
        
        # Encontrar las dos paradas entre las que estamos
        progress_per_stop = 100.0 / (len(route.stops) - 1)
        stop_index = int(route_progress / progress_per_stop)
        
        # Limitar índice
        if stop_index >= len(route.stops) - 1:
            stop_index = len(route.stops) - 2
        
        stop1 = route.stops[stop_index]
        stop2 = route.stops[stop_index + 1]
        
        # Calcular progreso entre estas dos paradas
        progress_in_segment = (route_progress % progress_per_stop) / progress_per_stop
        
        # Interpolar linealmente
        new_lat = stop1.latitude + (stop2.latitude - stop1.latitude) * progress_in_segment
        new_lon = stop1.longitude + (stop2.longitude - stop1.longitude) * progress_in_segment
        
        return new_lat, new_lon
    
    def _find_current_stop_index(self, location: Location, route: Route) -> int:
        """
        Encuentra el índice de la parada actual basado en el progreso.
        
        Args:
            location: Ubicación actual
            route: Recorrido
            
        Returns:
            Índice de la parada actual
        """
        if not route.stops:
            return 0
        
        progress_per_stop = 100.0 / (len(route.stops) - 1) if len(route.stops) > 1 else 100.0
        stop_index = int(location.route_progress / progress_per_stop)
        
        # Limitar índice
        if stop_index >= len(route.stops):
            stop_index = len(route.stops) - 1
        
        return stop_index
