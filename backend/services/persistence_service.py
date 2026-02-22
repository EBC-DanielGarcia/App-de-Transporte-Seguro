"""
Servicio de persistencia de datos en memoria.

Este servicio proporciona almacenamiento en memoria para:
- Ubicaciones con timestamp
- Cambios de estado
- Eventos de retraso
- Historial completo de eventos
- Cálculo de métricas
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4
from models import Location, TransportState, Delay, HistoryEvent, Metrics
from models.history_event import HistoryEventType


class PersistenceService:
    """
    Servicio de persistencia en memoria para datos de transporte.
    
    Almacena:
    - Ubicaciones con timestamp
    - Cambios de estado
    - Eventos de retraso
    - Historial completo de eventos
    """
    
    def __init__(self):
        """Inicializa el servicio de persistencia."""
        # Almacenamiento de ubicaciones: {transport_unit_id: [Location, ...]}
        self._locations: Dict[str, List[Location]] = {}
        
        # Almacenamiento de cambios de estado: {transport_unit_id: [HistoryEvent, ...]}
        self._state_changes: Dict[str, List[HistoryEvent]] = {}
        
        # Almacenamiento de eventos de retraso: {transport_unit_id: [Delay, ...]}
        self._delay_events: Dict[str, List[Delay]] = {}
        
        # Historial completo de eventos: {transport_unit_id: [HistoryEvent, ...]}
        self._history: Dict[str, List[HistoryEvent]] = {}
    
    def save_location_update(self, transport_unit_id: str, location: Location) -> None:
        """
        Guarda una actualización de ubicación con timestamp.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            location: Objeto Location con coordenadas y timestamp
        """
        if transport_unit_id not in self._locations:
            self._locations[transport_unit_id] = []
        
        self._locations[transport_unit_id].append(location)
        
        # También registrar en el historial
        history_event = HistoryEvent(
            id=str(uuid4()),
            transport_unit_id=transport_unit_id,
            event_type=HistoryEventType.LOCATION_UPDATE,
            timestamp=location.timestamp,
            data=location.to_dict()
        )
        self._add_to_history(transport_unit_id, history_event)
    
    def save_state_change(self, transport_unit_id: str, state: TransportState, 
                         old_state: Optional[TransportState] = None) -> None:
        """
        Guarda un cambio de estado con timestamp.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            state: Nuevo estado de la unidad
            old_state: Estado anterior (opcional)
        """
        if transport_unit_id not in self._state_changes:
            self._state_changes[transport_unit_id] = []
        
        # Crear evento de cambio de estado
        history_event = HistoryEvent(
            id=str(uuid4()),
            transport_unit_id=transport_unit_id,
            event_type=HistoryEventType.STATE_CHANGE,
            timestamp=datetime.now(),
            data={
                "old_state": str(old_state) if old_state else None,
                "new_state": str(state)
            }
        )
        
        self._state_changes[transport_unit_id].append(history_event)
        self._add_to_history(transport_unit_id, history_event)
    
    def save_delay_event(self, transport_unit_id: str, delay: Delay) -> None:
        """
        Guarda un evento de retraso.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            delay: Objeto Delay con información del retraso
        """
        if transport_unit_id not in self._delay_events:
            self._delay_events[transport_unit_id] = []
        
        self._delay_events[transport_unit_id].append(delay)
        
        # También registrar en el historial
        history_event = HistoryEvent(
            id=str(uuid4()),
            transport_unit_id=transport_unit_id,
            event_type=HistoryEventType.DELAY_DETECTED,
            timestamp=delay.detected_at,
            data=delay.to_dict()
        )
        self._add_to_history(transport_unit_id, history_event)
    
    def get_history(self, transport_unit_id: str) -> List[HistoryEvent]:
        """
        Recupera el historial completo de eventos de una unidad.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Lista de eventos ordenados cronológicamente
        """
        if transport_unit_id not in self._history:
            return []
        
        # Retornar ordenado por timestamp
        return sorted(
            self._history[transport_unit_id],
            key=lambda e: e.timestamp
        )
    
    def get_location_history(self, transport_unit_id: str) -> List[Location]:
        """
        Recupera el historial de ubicaciones de una unidad.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Lista de ubicaciones ordenadas por timestamp
        """
        if transport_unit_id not in self._locations:
            return []
        
        return sorted(
            self._locations[transport_unit_id],
            key=lambda l: l.timestamp
        )
    
    def get_state_change_history(self, transport_unit_id: str) -> List[HistoryEvent]:
        """
        Recupera el historial de cambios de estado de una unidad.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Lista de cambios de estado ordenados por timestamp
        """
        if transport_unit_id not in self._state_changes:
            return []
        
        return sorted(
            self._state_changes[transport_unit_id],
            key=lambda e: e.timestamp
        )
    
    def get_delay_history(self, transport_unit_id: str) -> List[Delay]:
        """
        Recupera el historial de retrasos de una unidad.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Lista de retrasos ordenados por timestamp
        """
        if transport_unit_id not in self._delay_events:
            return []
        
        return sorted(
            self._delay_events[transport_unit_id],
            key=lambda d: d.detected_at
        )
    
    def get_metrics(self, transport_unit_id: str) -> Metrics:
        """
        Calcula métricas finales para una unidad de transporte.
        
        Calcula:
        - Tiempo total de viaje
        - Tiempo total de retraso
        - Cantidad de retrasos
        - Retraso promedio
        - Porcentaje de puntualidad
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Objeto Metrics con las métricas calculadas
        """
        # Obtener historial de retrasos
        delays = self.get_delay_history(transport_unit_id)
        
        # Calcular tiempo total de retraso
        total_delay_time = sum(delay.magnitude for delay in delays)
        delay_count = len(delays)
        average_delay = total_delay_time / delay_count if delay_count > 0 else 0
        
        # Obtener historial de ubicaciones para calcular tiempo total
        locations = self.get_location_history(transport_unit_id)
        total_travel_time = 0
        
        if len(locations) >= 2:
            # Calcular diferencia entre primera y última ubicación
            first_location = locations[0]
            last_location = locations[-1]
            time_diff = last_location.timestamp - first_location.timestamp
            total_travel_time = int(time_diff.total_seconds() / 60)  # Convertir a minutos
        
        # Calcular porcentaje de puntualidad
        on_time_percentage = 0.0
        if total_travel_time > 0:
            on_time_percentage = ((total_travel_time - total_delay_time) / total_travel_time) * 100
            on_time_percentage = round(on_time_percentage, 1)
        
        return Metrics(
            transport_unit_id=transport_unit_id,
            total_travel_time=total_travel_time,
            total_delay_time=total_delay_time,
            delay_count=delay_count,
            average_delay=round(average_delay, 1),
            on_time_percentage=on_time_percentage
        )
    
    def clear_history(self, transport_unit_id: str) -> None:
        """
        Limpia el historial completo de una unidad (para testing).
        
        Args:
            transport_unit_id: ID de la unidad de transporte
        """
        if transport_unit_id in self._locations:
            del self._locations[transport_unit_id]
        if transport_unit_id in self._state_changes:
            del self._state_changes[transport_unit_id]
        if transport_unit_id in self._delay_events:
            del self._delay_events[transport_unit_id]
        if transport_unit_id in self._history:
            del self._history[transport_unit_id]
    
    def _add_to_history(self, transport_unit_id: str, event: HistoryEvent) -> None:
        """
        Añade un evento al historial general.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            event: Evento a añadir
        """
        if transport_unit_id not in self._history:
            self._history[transport_unit_id] = []
        
        self._history[transport_unit_id].append(event)
