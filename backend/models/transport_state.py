"""
Modelo de estado del transporte.
"""

from enum import Enum


class TransportState(Enum):
    """Estados posibles de una unidad de transporte."""
    
    EN_RUTA = "En_Ruta"
    DETENIDO = "Detenido"
    RETRASO = "Retraso"
    FUERA_SERVICIO = "Fuera_Servicio"
    
    def __str__(self):
        return self.value
