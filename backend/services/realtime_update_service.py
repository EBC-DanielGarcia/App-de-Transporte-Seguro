"""
Servicio de actualizaciones en tiempo real.

Mantiene sincronización entre backend y frontend mediante suscripciones a cambios
de ubicación, estado y eventos de retraso.
"""

from typing import Callable, Dict, List, Optional
from models.transport_unit import TransportUnit
from models.location import Location
from models.transport_state import TransportState
from models.delay import Delay


class RealtimeUpdateService:
    """
    Servicio que gestiona suscripciones a cambios en tiempo real.
    
    Permite que componentes se suscriban a cambios de ubicación, estado y retrasos,
    y transmite actualizaciones a todos los suscriptores.
    """
    
    def __init__(self):
        """Inicializa el servicio de actualizaciones en tiempo real."""
        # Diccionario de suscriptores por tipo de evento
        self._location_subscribers: Dict[str, List[Callable]] = {}
        self._state_subscribers: Dict[str, List[Callable]] = {}
        self._delay_subscribers: Dict[str, List[Callable]] = {}
        
        # Suscriptores globales (para todos los eventos)
        self._global_subscribers: List[Callable] = []
    
    def subscribe_to_location_updates(
        self,
        transport_unit_id: str,
        callback: Callable[[Location], None]
    ) -> None:
        """
        Suscribirse a cambios de ubicación de una unidad de transporte.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            callback: Función a llamar cuando cambia la ubicación
        """
        if transport_unit_id not in self._location_subscribers:
            self._location_subscribers[transport_unit_id] = []
        
        self._location_subscribers[transport_unit_id].append(callback)
    
    def subscribe_to_state_changes(
        self,
        transport_unit_id: str,
        callback: Callable[[TransportState], None]
    ) -> None:
        """
        Suscribirse a cambios de estado de una unidad de transporte.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            callback: Función a llamar cuando cambia el estado
        """
        if transport_unit_id not in self._state_subscribers:
            self._state_subscribers[transport_unit_id] = []
        
        self._state_subscribers[transport_unit_id].append(callback)
    
    def subscribe_to_delay_events(
        self,
        transport_unit_id: str,
        callback: Callable[[Delay], None]
    ) -> None:
        """
        Suscribirse a eventos de retraso de una unidad de transporte.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            callback: Función a llamar cuando se detecta un retraso
        """
        if transport_unit_id not in self._delay_subscribers:
            self._delay_subscribers[transport_unit_id] = []
        
        self._delay_subscribers[transport_unit_id].append(callback)
    
    def subscribe_to_all_updates(
        self,
        callback: Callable[[Dict], None]
    ) -> None:
        """
        Suscribirse a todos los eventos de actualización.
        
        Args:
            callback: Función a llamar para cualquier actualización
        """
        self._global_subscribers.append(callback)
    
    def broadcast_location_update(
        self,
        transport_unit_id: str,
        location: Location
    ) -> None:
        """
        Transmitir actualización de ubicación a todos los suscriptores.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            location: Nueva ubicación
        """
        # Notificar suscriptores específicos
        if transport_unit_id in self._location_subscribers:
            for callback in self._location_subscribers[transport_unit_id]:
                try:
                    callback(location)
                except Exception as e:
                    print(f"Error en callback de ubicación: {e}")
        
        # Notificar suscriptores globales
        for callback in self._global_subscribers:
            try:
                callback({
                    'type': 'location_update',
                    'transport_unit_id': transport_unit_id,
                    'location': location
                })
            except Exception as e:
                print(f"Error en callback global: {e}")
    
    def broadcast_state_change(
        self,
        transport_unit_id: str,
        new_state: TransportState,
        old_state: Optional[TransportState] = None
    ) -> None:
        """
        Transmitir cambio de estado a todos los suscriptores.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            new_state: Nuevo estado
            old_state: Estado anterior (opcional)
        """
        # Notificar suscriptores específicos
        if transport_unit_id in self._state_subscribers:
            for callback in self._state_subscribers[transport_unit_id]:
                try:
                    callback(new_state)
                except Exception as e:
                    print(f"Error en callback de estado: {e}")
        
        # Notificar suscriptores globales
        for callback in self._global_subscribers:
            try:
                callback({
                    'type': 'state_change',
                    'transport_unit_id': transport_unit_id,
                    'new_state': new_state,
                    'old_state': old_state
                })
            except Exception as e:
                print(f"Error en callback global: {e}")
    
    def broadcast_delay_event(
        self,
        transport_unit_id: str,
        delay: Delay
    ) -> None:
        """
        Transmitir evento de retraso a todos los suscriptores.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            delay: Evento de retraso detectado
        """
        # Notificar suscriptores específicos
        if transport_unit_id in self._delay_subscribers:
            for callback in self._delay_subscribers[transport_unit_id]:
                try:
                    callback(delay)
                except Exception as e:
                    print(f"Error en callback de retraso: {e}")
        
        # Notificar suscriptores globales
        for callback in self._global_subscribers:
            try:
                callback({
                    'type': 'delay_detected',
                    'transport_unit_id': transport_unit_id,
                    'delay': delay
                })
            except Exception as e:
                print(f"Error en callback global: {e}")
    
    def unsubscribe_from_location_updates(
        self,
        transport_unit_id: str,
        callback: Callable[[Location], None]
    ) -> None:
        """
        Desuscribirse de cambios de ubicación.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            callback: Función a remover
        """
        if transport_unit_id in self._location_subscribers:
            try:
                self._location_subscribers[transport_unit_id].remove(callback)
            except ValueError:
                pass
    
    def unsubscribe_from_state_changes(
        self,
        transport_unit_id: str,
        callback: Callable[[TransportState], None]
    ) -> None:
        """
        Desuscribirse de cambios de estado.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            callback: Función a remover
        """
        if transport_unit_id in self._state_subscribers:
            try:
                self._state_subscribers[transport_unit_id].remove(callback)
            except ValueError:
                pass
    
    def unsubscribe_from_delay_events(
        self,
        transport_unit_id: str,
        callback: Callable[[Delay], None]
    ) -> None:
        """
        Desuscribirse de eventos de retraso.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            callback: Función a remover
        """
        if transport_unit_id in self._delay_subscribers:
            try:
                self._delay_subscribers[transport_unit_id].remove(callback)
            except ValueError:
                pass
    
    def clear_all_subscribers(self) -> None:
        """Limpiar todos los suscriptores."""
        self._location_subscribers.clear()
        self._state_subscribers.clear()
        self._delay_subscribers.clear()
        self._global_subscribers.clear()
