"""
Modelo de parada.
"""

from dataclasses import dataclass, asdict


@dataclass
class Stop:
    """Representa una parada en el recorrido."""
    
    id: str
    name: str
    latitude: float
    longitude: float
    distance_from_start: float  # en km
    estimated_stop_duration: int  # en segundos
    
    def to_dict(self):
        """Convierte la parada a diccionario."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        """Crea una parada desde un diccionario."""
        return cls(**data)
