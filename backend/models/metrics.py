"""
Modelo de métricas.
"""

from dataclasses import dataclass, asdict


@dataclass
class Metrics:
    """Representa las métricas de desempeño de una unidad de transporte."""
    
    transport_unit_id: str
    total_travel_time: int  # en minutos
    total_delay_time: int  # en minutos
    delay_count: int  # número de retrasos detectados
    average_delay: float  # en minutos
    on_time_percentage: float  # 0-100
    
    def to_dict(self):
        """Convierte las métricas a diccionario."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        """Crea métricas desde un diccionario."""
        return cls(**data)
