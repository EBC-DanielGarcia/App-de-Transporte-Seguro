"""
Modelo de unidad de transporte.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from .location import Location
from .transport_state import TransportState


@dataclass
class TransportUnit:
    """Representa una unidad de transporte."""
    
    id: str
    name: str
    route_id: str
    current_location: Location
    state: TransportState
    speed: float  # en km/h
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self):
        """Convierte la unidad de transporte a diccionario."""
        data = asdict(self)
        data['current_location'] = self.current_location.to_dict()
        data['state'] = self.state.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crea una unidad de transporte desde un diccionario."""
        data_copy = data.copy()
        
        # Convertir location
        if isinstance(data_copy['current_location'], dict):
            data_copy['current_location'] = Location.from_dict(data_copy['current_location'])
        
        # Convertir state
        if isinstance(data_copy['state'], str):
            data_copy['state'] = TransportState(data_copy['state'])
        
        # Convertir timestamps
        if isinstance(data_copy['created_at'], str):
            data_copy['created_at'] = datetime.fromisoformat(data_copy['created_at'])
        if isinstance(data_copy['updated_at'], str):
            data_copy['updated_at'] = datetime.fromisoformat(data_copy['updated_at'])
        
        return cls(**data_copy)
