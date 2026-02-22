"""
Servicio de historial de eventos.

Recupera historial de cambios de estado, eventos de retraso y calcula métricas
de desempeño del transporte.
"""

from typing import List, Optional
from datetime import datetime
from models.history_event import HistoryEvent
from models.metrics import Metrics
from models.transport_state import TransportState
from models.delay import Delay
from services.persistence_service import PersistenceService


class HistoryService:
    """
    Servicio que gestiona el historial de eventos y cálculo de métricas.
    
    Proporciona acceso a:
    - Historial de cambios de estado en orden cronológico
    - Historial de eventos de retraso
    - Métricas de desempeño (tiempo total, retrasos acumulados)
    """
    
    def __init__(self, persistence_service: PersistenceService):
        """
        Inicializa el servicio de historial.
        
        Args:
            persistence_service: Servicio de persistencia para acceder a datos
        """
        self.persistence_service = persistence_service
    
    def get_history(self, transport_unit_id: str) -> List[HistoryEvent]:
        """
        Obtener historial completo de eventos en orden cronológico.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Lista de eventos ordenados cronológicamente
        """
        history = self.persistence_service.get_history(transport_unit_id)
        
        # Ordenar por timestamp de forma cronológica
        sorted_history = sorted(
            history,
            key=lambda event: event.timestamp
        )
        
        return sorted_history
    
    def get_state_changes(self, transport_unit_id: str) -> List[HistoryEvent]:
        """
        Obtener solo los cambios de estado en orden cronológico.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Lista de eventos de cambio de estado
        """
        history = self.get_history(transport_unit_id)
        
        # Filtrar solo eventos de cambio de estado
        state_changes = [
            event for event in history
            if event.type == "STATE_CHANGE"
        ]
        
        return state_changes
    
    def get_delay_events(self, transport_unit_id: str) -> List[HistoryEvent]:
        """
        Obtener solo los eventos de retraso en orden cronológico.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Lista de eventos de retraso
        """
        history = self.get_history(transport_unit_id)
        
        # Filtrar solo eventos de retraso
        delay_events = [
            event for event in history
            if event.type == "DELAY_DETECTED"
        ]
        
        return delay_events
    
    def get_location_updates(self, transport_unit_id: str) -> List[HistoryEvent]:
        """
        Obtener solo las actualizaciones de ubicación en orden cronológico.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Lista de eventos de actualización de ubicación
        """
        history = self.get_history(transport_unit_id)
        
        # Filtrar solo eventos de actualización de ubicación
        location_updates = [
            event for event in history
            if event.type == "LOCATION_UPDATE"
        ]
        
        return location_updates
    
    def calculate_metrics(self, transport_unit_id: str) -> Metrics:
        """
        Calcular métricas de desempeño para una unidad de transporte.
        
        Calcula:
        - Tiempo total de viaje
        - Tiempo total de retrasos
        - Cantidad de retrasos detectados
        - Retraso promedio
        - Porcentaje de puntualidad
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Objeto Metrics con las métricas calculadas
        """
        history = self.get_history(transport_unit_id)
        
        if not history:
            # Si no hay historial, retornar métricas vacías
            return Metrics(
                transport_unit_id=transport_unit_id,
                total_travel_time=0,
                total_delay_time=0,
                delay_count=0,
                average_delay=0,
                on_time_percentage=100
            )
        
        # Obtener primer y último evento para calcular tiempo total
        first_event = history[0]
        last_event = history[-1]
        
        total_travel_time = int(
            (last_event.timestamp - first_event.timestamp).total_seconds() / 60
        )
        
        # Obtener eventos de retraso
        delay_events = self.get_delay_events(transport_unit_id)
        
        # Calcular tiempo total de retrasos
        total_delay_time = 0
        for event in delay_events:
            if 'delay' in event.data and isinstance(event.data['delay'], dict):
                magnitude = event.data['delay'].get('magnitude', 0)
                total_delay_time += magnitude
        
        # Cantidad de retrasos
        delay_count = len(delay_events)
        
        # Retraso promedio
        average_delay = (
            total_delay_time / delay_count if delay_count > 0 else 0
        )
        
        # Porcentaje de puntualidad
        on_time_percentage = (
            100 - (total_delay_time / total_travel_time * 100)
            if total_travel_time > 0 else 100
        )
        on_time_percentage = max(0, min(100, on_time_percentage))
        
        return Metrics(
            transport_unit_id=transport_unit_id,
            total_travel_time=total_travel_time,
            total_delay_time=total_delay_time,
            delay_count=delay_count,
            average_delay=average_delay,
            on_time_percentage=on_time_percentage
        )
    
    def get_current_state_from_history(
        self,
        transport_unit_id: str
    ) -> Optional[TransportState]:
        """
        Obtener el estado actual basado en el último cambio de estado en el historial.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Estado actual o None si no hay historial
        """
        state_changes = self.get_state_changes(transport_unit_id)
        
        if not state_changes:
            return None
        
        # El último cambio de estado es el estado actual
        last_state_change = state_changes[-1]
        
        if 'new_state' in last_state_change.data:
            return last_state_change.data['new_state']
        
        return None
    
    def get_events_between(
        self,
        transport_unit_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[HistoryEvent]:
        """
        Obtener eventos dentro de un rango de tiempo.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            start_time: Tiempo de inicio
            end_time: Tiempo de fin
            
        Returns:
            Lista de eventos dentro del rango
        """
        history = self.get_history(transport_unit_id)
        
        filtered_events = [
            event for event in history
            if start_time <= event.timestamp <= end_time
        ]
        
        return filtered_events
    
    def get_summary(self, transport_unit_id: str) -> dict:
        """
        Obtener resumen completo del historial y métricas.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Diccionario con resumen completo
        """
        history = self.get_history(transport_unit_id)
        state_changes = self.get_state_changes(transport_unit_id)
        delay_events = self.get_delay_events(transport_unit_id)
        metrics = self.calculate_metrics(transport_unit_id)
        
        return {
            'transport_unit_id': transport_unit_id,
            'total_events': len(history),
            'state_changes': len(state_changes),
            'delay_events': len(delay_events),
            'metrics': {
                'total_travel_time': metrics.total_travel_time,
                'total_delay_time': metrics.total_delay_time,
                'delay_count': metrics.delay_count,
                'average_delay': metrics.average_delay,
                'on_time_percentage': metrics.on_time_percentage
            },
            'first_event': history[0].timestamp.isoformat() if history else None,
            'last_event': history[-1].timestamp.isoformat() if history else None
        }
