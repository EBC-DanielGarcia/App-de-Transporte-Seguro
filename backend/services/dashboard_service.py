"""
Servicio de dashboard.

Proporciona datos agregados para el dashboard, incluyendo lista de unidades,
filtrado, ordenamiento y detalles completos.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from models.transport_unit import TransportUnit
from models.transport_state import TransportState
from services.route_service import RouteService
from services.eta_calculator import ETACalculator
from services.history_service import HistoryService


class SortBy(Enum):
    """Opciones de ordenamiento para unidades de transporte."""
    ETA = "eta"
    STATE = "state"
    NAME = "name"
    DISTANCE = "distance"


class DashboardService:
    """
    Servicio que proporciona datos para el dashboard.
    
    Proporciona:
    - Lista de unidades con filtrado y ordenamiento
    - Detalles completos de una unidad
    - Datos agregados para visualización
    """
    
    def __init__(
        self,
        route_service: RouteService,
        eta_calculator: ETACalculator,
        history_service: HistoryService
    ):
        """
        Inicializa el servicio de dashboard.
        
        Args:
            route_service: Servicio de rutas
            eta_calculator: Calculadora de ETA
            history_service: Servicio de historial
        """
        self.route_service = route_service
        self.eta_calculator = eta_calculator
        self.history_service = history_service
        self._transport_units: Dict[str, TransportUnit] = {}
    
    def add_transport_unit(self, unit: TransportUnit) -> None:
        """
        Agregar una unidad de transporte al dashboard.
        
        Args:
            unit: Unidad de transporte a agregar
        """
        self._transport_units[unit.id] = unit
    
    def get_transport_unit(self, unit_id: str) -> Optional[TransportUnit]:
        """
        Obtener una unidad de transporte.
        
        Args:
            unit_id: ID de la unidad
            
        Returns:
            Unidad de transporte o None
        """
        return self._transport_units.get(unit_id)
    
    def get_all_transport_units(self) -> List[TransportUnit]:
        """
        Obtener todas las unidades de transporte.
        
        Returns:
            Lista de todas las unidades
        """
        return list(self._transport_units.values())
    
    def filter_by_state(
        self,
        state: TransportState
    ) -> List[TransportUnit]:
        """
        Filtrar unidades por estado.
        
        Args:
            state: Estado a filtrar
            
        Returns:
            Lista de unidades con el estado especificado
        """
        return [
            unit for unit in self._transport_units.values()
            if unit.state == state
        ]
    
    def filter_by_states(
        self,
        states: List[TransportState]
    ) -> List[TransportUnit]:
        """
        Filtrar unidades por múltiples estados.
        
        Args:
            states: Lista de estados a filtrar
            
        Returns:
            Lista de unidades con alguno de los estados especificados
        """
        return [
            unit for unit in self._transport_units.values()
            if unit.state in states
        ]
    
    def sort_units(
        self,
        units: List[TransportUnit],
        sort_by: SortBy = SortBy.ETA,
        reverse: bool = False
    ) -> List[TransportUnit]:
        """
        Ordenar unidades de transporte.
        
        Args:
            units: Lista de unidades a ordenar
            sort_by: Criterio de ordenamiento
            reverse: Si True, ordena en orden descendente
            
        Returns:
            Lista ordenada de unidades
        """
        if sort_by == SortBy.ETA:
            # Ordenar por ETA (menor primero)
            return sorted(
                units,
                key=lambda u: self._get_min_eta(u),
                reverse=reverse
            )
        elif sort_by == SortBy.STATE:
            # Ordenar por estado
            state_order = {
                TransportState.EN_RUTA: 0,
                TransportState.DETENIDO: 1,
                TransportState.RETRASO: 2,
                TransportState.FUERA_SERVICIO: 3
            }
            return sorted(
                units,
                key=lambda u: state_order.get(u.state, 999),
                reverse=reverse
            )
        elif sort_by == SortBy.NAME:
            # Ordenar por nombre
            return sorted(
                units,
                key=lambda u: u.name,
                reverse=reverse
            )
        elif sort_by == SortBy.DISTANCE:
            # Ordenar por distancia recorrida
            return sorted(
                units,
                key=lambda u: u.current_location.route_progress,
                reverse=reverse
            )
        
        return units
    
    def get_unit_details(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener detalles completos de una unidad.
        
        Args:
            unit_id: ID de la unidad
            
        Returns:
            Diccionario con detalles completos o None
        """
        unit = self.get_transport_unit(unit_id)
        if unit is None:
            return None
        
        route = self.route_service.get_route(unit.route_id)
        if route is None:
            return None
        
        # Obtener parada actual y siguiente
        current_stop = self.route_service.find_current_stop(
            unit.route_id,
            unit.current_location.route_progress
        )
        next_stop = self.route_service.find_next_stop(
            unit.route_id,
            unit.current_location.route_progress
        )
        
        # Obtener ETAs para todas las paradas
        etas = self.eta_calculator.recalculate_all_etas(
            transport_unit_id=unit.id,
            current_location=unit.current_location,
            route=route,
            speed=unit.speed
            )


        
        # Obtener historial y métricas
        history = self.history_service.get_history(unit_id)
        metrics = self.history_service.calculate_metrics(unit_id)
        
        return {
            'id': unit.id,
            'name': unit.name,
            'route_id': unit.route_id,
            'route_name': route.name,
            'current_location': {
                'latitude': unit.current_location.latitude,
                'longitude': unit.current_location.longitude,
                'route_progress': unit.current_location.route_progress,
                'timestamp': unit.current_location.timestamp.isoformat()
            },
            'state': unit.state.value,
            'speed': unit.speed,
            'current_stop': {
                'id': current_stop.id,
                'name': current_stop.name,
                'distance_from_start': current_stop.distance_from_start
            } if current_stop else None,
            'next_stop': {
                'id': next_stop.id,
                'name': next_stop.name,
                'distance_from_start': next_stop.distance_from_start,
                'eta': etas.get(next_stop.id, 0)
            } if next_stop else None,
            'etas': {
                stop_id: eta for stop_id, eta in etas.items()
            },
            'history_count': len(history),
            'metrics': {
                'total_travel_time': metrics.total_travel_time,
                'total_delay_time': metrics.total_delay_time,
                'delay_count': metrics.delay_count,
                'average_delay': metrics.average_delay,
                'on_time_percentage': metrics.on_time_percentage
            },
            'created_at': unit.created_at.isoformat(),
            'updated_at': unit.updated_at.isoformat()
        }
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen del dashboard con estadísticas generales.
        
        Returns:
            Diccionario con resumen del dashboard
        """
        units = self.get_all_transport_units()
        
        # Contar unidades por estado
        state_counts = {
            TransportState.EN_RUTA: 0,
            TransportState.DETENIDO: 0,
            TransportState.RETRASO: 0,
            TransportState.FUERA_SERVICIO: 0
        }
        
        for unit in units:
            state_counts[unit.state] += 1
        
        # Calcular promedio de retrasos
        total_delays = 0
        units_with_delays = 0
        
        for unit in units:
            metrics = self.history_service.calculate_metrics(unit.id)
            if metrics.delay_count > 0:
                total_delays += metrics.total_delay_time
                units_with_delays += 1
        
        average_delay = (
            total_delays / units_with_delays if units_with_delays > 0 else 0
        )
        
        return {
            'total_units': len(units),
            'units_by_state': {
                'en_ruta': state_counts[TransportState.EN_RUTA],
                'detenido': state_counts[TransportState.DETENIDO],
                'retraso': state_counts[TransportState.RETRASO],
                'fuera_servicio': state_counts[TransportState.FUERA_SERVICIO]
            },
            'units_with_delays': units_with_delays,
            'average_delay_minutes': average_delay
        }
    
    def _get_min_eta(self, unit: TransportUnit) -> float:
        
        """
        Obtener el ETA mínimo para una unidad (a la siguiente parada).
        
        Args:
            unit: Unidad de transporte
            
        Returns:
            ETA mínimo en minutos
        """
        
        route = self.route_service.get_route(unit.route_id)
        if route is None:
            return float("inf")
        
        etas = self.eta_calculator.recalculate_all_etas(
            transport_unit_id=unit.id,
            current_location=unit.current_location,
            route=route,
            speed=unit.speed
            )


        
        if not etas:
            return float('inf')
        
        return min(etas.values())
