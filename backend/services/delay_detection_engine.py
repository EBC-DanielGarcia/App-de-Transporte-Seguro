"""
Motor de detección de retrasos.

Este servicio proporciona:
- Comparación de tiempo real con tiempo estimado
- Detección automática de retrasos
- Cálculo de magnitud del retraso en minutos
- Actualización de estado por retraso
- Persistencia de eventos de retraso
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4
from models import Location, Route, Stop, TransportState, Delay, TransportUnit
from services.eta_calculator import ETACalculator
from services.persistence_service import PersistenceService


class DelayDetectionEngine:
    """
    Motor de detección de retrasos.
    
    Detecta:
    - Retrasos comparando tiempo real con tiempo estimado
    - Magnitud del retraso en minutos
    - Actualiza estado del transporte a "Retraso"
    - Persiste eventos de retraso
    """
    
    def __init__(self, eta_calculator: ETACalculator, persistence_service: PersistenceService):
        """
        Inicializa el motor de detección de retrasos.
        
        Args:
            eta_calculator: Calculadora de ETA
            persistence_service: Servicio de persistencia
        """
        self.eta_calculator = eta_calculator
        self.persistence_service = persistence_service
        
        # Registro de tiempos de llegada reales: {transport_unit_id: {stop_id: timestamp}}
        self._arrival_times: Dict[str, Dict[str, datetime]] = {}
        
        # Registro de retrasos detectados: {transport_unit_id: [Delay, ...]}
        self._detected_delays: Dict[str, List[Delay]] = {}
        
        # Estado de retraso actual: {transport_unit_id: is_delayed}
        self._delay_status: Dict[str, bool] = {}
    
    def check_for_delays(
        self,
        transport_unit_id: str,
        current_location: Location,
        route: Route,
        speed: float,
        current_stop: Optional[Stop] = None
    ) -> List[Delay]:
        """
        Detecta retrasos comparando tiempo real con tiempo estimado.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            current_location: Ubicación actual
            route: Recorrido
            speed: Velocidad promedio en km/h
            current_stop: Parada actual (opcional)
            
        Returns:
            Lista de retrasos detectados
        """
        detected_delays = []
        
        if not current_stop:
            return detected_delays
        
        # Obtener ETA para la parada actual
        eta_minutes = self.eta_calculator.calculate_eta(
            current_location,
            current_stop,
            speed
        )
        
        # Registrar tiempo de llegada actual
        if transport_unit_id not in self._arrival_times:
            self._arrival_times[transport_unit_id] = {}
        
        self._arrival_times[transport_unit_id][current_stop.id] = datetime.now()
        
        # Comparar con ETA anterior si existe
        previous_eta = self.eta_calculator.get_cached_eta(transport_unit_id, current_stop.id)
        
        if previous_eta is not None:
            # Calcular retraso: si tiempo real > ETA, hay retraso
            # Aquí asumimos que si el ETA cambió significativamente, hay retraso
            delay_magnitude = max(0, previous_eta - eta_minutes)
            
            if delay_magnitude > 0:
                # Crear evento de retraso
                delay = Delay(
                    id=str(uuid4()),
                    transport_unit_id=transport_unit_id,
                    detected_at=datetime.now(),
                    magnitude=int(delay_magnitude),
                    affected_stop=current_stop,
                    reason="Retraso detectado por cambio en ETA"
                )
                
                detected_delays.append(delay)
                
                # Guardar en registro
                if transport_unit_id not in self._detected_delays:
                    self._detected_delays[transport_unit_id] = []
                self._detected_delays[transport_unit_id].append(delay)
                
                # Persistir evento
                self.persistence_service.save_delay_event(transport_unit_id, delay)
                
                # Actualizar estado de retraso
                self._delay_status[transport_unit_id] = True
        
        return detected_delays
    
    def update_delay_status(
        self,
        transport_unit_id: str,
        transport_unit: TransportUnit
    ) -> Optional[TransportState]:
        """
        Actualiza el estado de la unidad si hay retraso detectado.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            transport_unit: Objeto TransportUnit a actualizar
            
        Returns:
            Nuevo estado si cambió, None si no cambió
        """
        is_delayed = self._delay_status.get(transport_unit_id, False)
        
        if is_delayed and transport_unit.state != TransportState.RETRASO:
            # Cambiar estado a Retraso
            old_state = transport_unit.state
            transport_unit.state = TransportState.RETRASO
            transport_unit.updated_at = datetime.now()
            
            # Persistir cambio de estado
            self.persistence_service.save_state_change(
                transport_unit_id,
                TransportState.RETRASO,
                old_state
            )
            
            return TransportState.RETRASO
        
        elif not is_delayed and transport_unit.state == TransportState.RETRASO:
            # Cambiar estado de vuelta a En_Ruta
            old_state = transport_unit.state
            transport_unit.state = TransportState.EN_RUTA
            transport_unit.updated_at = datetime.now()
            
            # Persistir cambio de estado
            self.persistence_service.save_state_change(
                transport_unit_id,
                TransportState.EN_RUTA,
                old_state
            )
            
            return TransportState.EN_RUTA
        
        return None
    
    def get_delay_magnitude(self, transport_unit_id: str) -> int:
        """
        Obtiene la magnitud total del retraso para una unidad.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Magnitud total del retraso en minutos
        """
        if transport_unit_id not in self._detected_delays:
            return 0
        
        delays = self._detected_delays[transport_unit_id]
        total_magnitude = sum(delay.magnitude for delay in delays)
        
        return total_magnitude
    
    def get_detected_delays(self, transport_unit_id: str) -> List[Delay]:
        """
        Obtiene todos los retrasos detectados para una unidad.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            Lista de retrasos detectados
        """
        return self._detected_delays.get(transport_unit_id, [])
    
    def is_delayed(self, transport_unit_id: str) -> bool:
        """
        Verifica si una unidad está retrasada.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            
        Returns:
            True si está retrasada, False en caso contrario
        """
        return self._delay_status.get(transport_unit_id, False)
    
    def clear_delay_status(self, transport_unit_id: str) -> None:
        """
        Limpia el estado de retraso para una unidad (para testing).
        
        Args:
            transport_unit_id: ID de la unidad de transporte
        """
        if transport_unit_id in self._delay_status:
            del self._delay_status[transport_unit_id]
        if transport_unit_id in self._detected_delays:
            del self._detected_delays[transport_unit_id]
        if transport_unit_id in self._arrival_times:
            del self._arrival_times[transport_unit_id]
