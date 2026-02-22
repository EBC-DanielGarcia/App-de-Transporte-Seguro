"""
Servicio de gestión de rutas.

Gestiona rutas predefinidas, paradas y búsqueda de parada actual/siguiente.
"""

from typing import List, Optional, Tuple
from models.route import Route
from models.stop import Stop
from models.location import Location


class RouteService:
    """
    Servicio que gestiona rutas y paradas.
    
    Proporciona:
    - Almacenamiento de rutas predefinidas
    - Búsqueda de parada actual/siguiente
    - Cálculo de distancia entre paradas
    - Información de recorrido
    """
    
    def __init__(self):
        """Inicializa el servicio de rutas."""
        self._routes: dict[str, Route] = {}
    
    def add_route(self, route: Route) -> None:
        """
        Agregar una ruta al servicio.
        
        Args:
            route: Ruta a agregar
        """
        self._routes[route.id] = route
    
    def get_route(self, route_id: str) -> Optional[Route]:
        """
        Obtener una ruta por ID.
        
        Args:
            route_id: ID de la ruta
            
        Returns:
            Ruta o None si no existe
        """
        return self._routes.get(route_id)
    
    def get_all_routes(self) -> List[Route]:
        """
        Obtener todas las rutas.
        
        Returns:
            Lista de todas las rutas
        """
        return list(self._routes.values())
    
    def get_stops_for_route(self, route_id: str) -> Optional[List[Stop]]:
        """
        Obtener todas las paradas de una ruta.
        
        Args:
            route_id: ID de la ruta
            
        Returns:
            Lista de paradas o None si la ruta no existe
        """
        route = self.get_route(route_id)
        if route is None:
            return None
        
        return route.stops
    
    def get_stop(self, route_id: str, stop_id: str) -> Optional[Stop]:
        """
        Obtener una parada específica de una ruta.
        
        Args:
            route_id: ID de la ruta
            stop_id: ID de la parada
            
        Returns:
            Parada o None si no existe
        """
        stops = self.get_stops_for_route(route_id)
        if stops is None:
            return None
        
        for stop in stops:
            if stop.id == stop_id:
                return stop
        
        return None
    
    def find_current_stop(
        self,
        route_id: str,
        route_progress: float
    ) -> Optional[Stop]:
        """
        Encontrar la parada actual basada en el progreso en la ruta.
        
        Args:
            route_id: ID de la ruta
            route_progress: Progreso en la ruta (0-100)
            
        Returns:
            Parada actual o None
        """
        stops = self.get_stops_for_route(route_id)
        if stops is None or not stops:
            return None
        
        route = self.get_route(route_id)
        if route is None:
            return None
        
        # Calcular distancia actual basada en progreso
        current_distance = (route_progress / 100) * route.total_distance
        
        # Encontrar parada actual (la más cercana sin exceder la distancia actual)
        current_stop = None
        for stop in stops:
            if stop.distance_from_start <= current_distance:
                current_stop = stop
            else:
                break
        
        return current_stop
    
    def find_next_stop(
        self,
        route_id: str,
        route_progress: float
    ) -> Optional[Stop]:
        """
        Encontrar la siguiente parada basada en el progreso en la ruta.
        
        Args:
            route_id: ID de la ruta
            route_progress: Progreso en la ruta (0-100)
            
        Returns:
            Siguiente parada o None si ya llegó al final
        """
        stops = self.get_stops_for_route(route_id)
        if stops is None or not stops:
            return None
        
        route = self.get_route(route_id)
        if route is None:
            return None
        
        # Calcular distancia actual basada en progreso
        current_distance = (route_progress / 100) * route.total_distance
        
        # Encontrar siguiente parada (la primera que excede la distancia actual)
        for stop in stops:
            if stop.distance_from_start > current_distance:
                return stop
        
        return None
    
    def get_stops_until_destination(
        self,
        route_id: str,
        route_progress: float
    ) -> List[Stop]:
        """
        Obtener todas las paradas desde la posición actual hasta el final.
        
        Args:
            route_id: ID de la ruta
            route_progress: Progreso en la ruta (0-100)
            
        Returns:
            Lista de paradas restantes
        """
        stops = self.get_stops_for_route(route_id)
        if stops is None:
            return []
        
        route = self.get_route(route_id)
        if route is None:
            return []
        
        # Calcular distancia actual basada en progreso
        current_distance = (route_progress / 100) * route.total_distance
        
        # Obtener paradas desde la posición actual
        remaining_stops = [
            stop for stop in stops
            if stop.distance_from_start >= current_distance
        ]
        
        return remaining_stops
    
    def calculate_distance_to_stop(
        self,
        route_id: str,
        route_progress: float,
        target_stop_id: str
    ) -> Optional[float]:
        """
        Calcular distancia desde la posición actual a una parada destino.
        
        Args:
            route_id: ID de la ruta
            route_progress: Progreso en la ruta (0-100)
            target_stop_id: ID de la parada destino
            
        Returns:
            Distancia en km o None si no existe la parada
        """
        route = self.get_route(route_id)
        if route is None:
            return None
        
        target_stop = self.get_stop(route_id, target_stop_id)
        if target_stop is None:
            return None
        
        # Calcular distancia actual basada en progreso
        current_distance = (route_progress / 100) * route.total_distance
        
        # Calcular distancia a la parada destino
        distance_to_stop = target_stop.distance_from_start - current_distance
        
        # Si la distancia es negativa, ya pasamos la parada
        if distance_to_stop < 0:
            return 0
        
        return distance_to_stop
    
    def get_route_progress_at_stop(
        self,
        route_id: str,
        stop_id: str
    ) -> Optional[float]:
        """
        Obtener el progreso en la ruta (0-100) en una parada específica.
        
        Args:
            route_id: ID de la ruta
            stop_id: ID de la parada
            
        Returns:
            Progreso (0-100) o None si no existe la parada
        """
        route = self.get_route(route_id)
        if route is None:
            return None
        
        stop = self.get_stop(route_id, stop_id)
        if stop is None:
            return None
        
        if route.total_distance == 0:
            return 0
        
        progress = (stop.distance_from_start / route.total_distance) * 100
        return min(100, max(0, progress))
    
    def get_route_info(self, route_id: str) -> Optional[dict]:
        """
        Obtener información completa de una ruta.
        
        Args:
            route_id: ID de la ruta
            
        Returns:
            Diccionario con información de la ruta o None
        """
        route = self.get_route(route_id)
        if route is None:
            return None
        
        return {
            'id': route.id,
            'name': route.name,
            'total_distance': route.total_distance,
            'estimated_duration': route.estimated_duration,
            'stops_count': len(route.stops),
            'stops': [
                {
                    'id': stop.id,
                    'name': stop.name,
                    'latitude': stop.latitude,
                    'longitude': stop.longitude,
                    'distance_from_start': stop.distance_from_start,
                    'estimated_stop_duration': stop.estimated_stop_duration
                }
                for stop in route.stops
            ]
        }
