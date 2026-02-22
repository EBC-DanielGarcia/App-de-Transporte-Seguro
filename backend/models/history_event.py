"""
Modelo de evento de historial.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class HistoryEventType(Enum):
    """Tipos de eventos que se pueden registrar en el historial."""
    
    STATE_CHANGE = "STATE_CHANGE"
    LOCATION_UPDATE = "LOCATION_UPDATE"
    DELAY_DETECTED = "DELAY_DETECTED"


@dataclass
class HistoryEvent:
    """Representa un evento en el historial de una unidad de transporte."""
    
    id: str
    transport_unit_id: str
    event_type: HistoryEventType
    timestamp: datetime
    data: Optional[Any] = None
    
    def to_dict(self):
        """Convierte el evento a diccionario."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crea un evento desde un diccionario."""
        data_copy = data.copy()
        
        # Convertir event_type
        if isinstance(data_copy['event_type'], str):
            data_copy['event_type'] = HistoryEventType(data_copy['event_type'])
        
        # Convertir timestamp
        if isinstance(data_copy['timestamp'], str):
            data_copy['timestamp'] = datetime.fromisoformat(data_copy['timestamp'])
        
        return cls(**data_copy)
