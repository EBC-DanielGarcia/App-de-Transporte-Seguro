"""
Modelo de retraso.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from .stop import Stop


@dataclass
class Delay:
    """Representa un retraso detectado."""
    
    id: str
    transport_unit_id: str
    detected_at: datetime
    magnitude: int  # en minutos
    affected_stop: Stop
    reason: Optional[str] = None
    
    def to_dict(self):
        """Convierte el retraso a diccionario."""
        data = asdict(self)
        data['detected_at'] = self.detected_at.isoformat()
        data['affected_stop'] = self.affected_stop.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crea un retraso desde un diccionario."""
        data_copy = data.copy()
        
        # Convertir detected_at
        if isinstance(data_copy['detected_at'], str):
            data_copy['detected_at'] = datetime.fromisoformat(data_copy['detected_at'])
        
        # Convertir affected_stop
        if isinstance(data_copy['affected_stop'], dict):
            data_copy['affected_stop'] = Stop.from_dict(data_copy['affected_stop'])
        
        return cls(**data_copy)
