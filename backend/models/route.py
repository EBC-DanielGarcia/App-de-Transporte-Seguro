"""
Modelo de recorrido.
"""

from dataclasses import dataclass, asdict, field
from typing import List
from .stop import Stop


@dataclass
class Route:
    """Representa un recorrido con sus paradas."""
    
    id: str
    name: str
    stops: List[Stop] = field(default_factory=list)
    total_distance: float = 0.0  # en km
    estimated_duration: int = 0  # en minutos
    
    def to_dict(self):
        """Convierte el recorrido a diccionario."""
        data = asdict(self)
        data['stops'] = [stop.to_dict() if isinstance(stop, Stop) else stop 
                         for stop in self.stops]
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crea un recorrido desde un diccionario."""
        data_copy = data.copy()
        if 'stops' in data_copy:
            data_copy['stops'] = [
                Stop.from_dict(stop) if isinstance(stop, dict) else stop
                for stop in data_copy['stops']
            ]
        return cls(**data_copy)
