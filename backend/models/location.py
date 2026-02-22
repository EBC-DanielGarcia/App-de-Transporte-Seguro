"""
Modelo de ubicación.
"""

from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Location:
    """Representa la ubicación de una unidad de transporte."""
    
    latitude: float
    longitude: float
    route_progress: float  # 0-100, porcentaje de avance en el recorrido
    timestamp: datetime
    
    def to_dict(self):
        """Convierte la ubicación a diccionario."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crea una ubicación desde un diccionario."""
        data_copy = data.copy()
        if isinstance(data_copy['timestamp'], str):
            data_copy['timestamp'] = datetime.fromisoformat(data_copy['timestamp'])
        return cls(**data_copy)
