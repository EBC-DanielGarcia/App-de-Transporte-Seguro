"""
Servidor WebSocket para actualizaciones en tiempo real.

Proporciona conexión WebSocket para que los clientes reciban actualizaciones
de ubicación, cambios de estado y eventos de retraso en tiempo real.
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from typing import Dict, Set


class WebSocketServer:
    """
    Servidor WebSocket para actualizaciones en tiempo real.
    
    Gestiona conexiones de clientes y transmite eventos de actualización.
    """
    
    def __init__(self, app, realtime_update_service):
        """
        Inicializa el servidor WebSocket.
        
        Args:
            app: Aplicación Flask
            realtime_update_service: Servicio de actualizaciones en tiempo real
        """
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading'
        )
        self.realtime_update_service = realtime_update_service
        
        # Almacenar clientes conectados por unidad de transporte
        self.unit_subscribers: Dict[str, Set[str]] = {}
        
        # Registrar event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Registrar manejadores de eventos WebSocket."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Manejar conexión de cliente."""
            print(f'Cliente conectado: {self.socketio.server.environ.get("REMOTE_ADDR")}')
            emit('connection_response', {
                'status': 'connected',
                'timestamp': datetime.now().isoformat(),
                'message': 'Conectado al servidor de monitoreo de transporte'
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Manejar desconexión de cliente."""
            print(f'Cliente desconectado')
        
        @self.socketio.on('subscribe_to_unit')
        def handle_subscribe_to_unit(data):
            """
            Manejar suscripción a actualizaciones de una unidad.
            
            Datos esperados:
            {
                "transport_unit_id": "unit-1"
            }
            """
            unit_id = data.get('transport_unit_id')
            if not unit_id:
                emit('error', {'message': 'Falta transport_unit_id'})
                return
            
            # Unirse a sala específica de la unidad
            join_room(f'unit_{unit_id}')
            
            # Registrar suscriptor
            if unit_id not in self.unit_subscribers:
                self.unit_subscribers[unit_id] = set()
            
            self.unit_subscribers[unit_id].add(self.socketio.server.environ.get('REMOTE_ADDR'))
            
            emit('subscription_response', {
                'status': 'subscribed',
                'transport_unit_id': unit_id,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('unsubscribe_from_unit')
        def handle_unsubscribe_from_unit(data):
            """
            Manejar desuscripción de actualizaciones de una unidad.
            
            Datos esperados:
            {
                "transport_unit_id": "unit-1"
            }
            """
            unit_id = data.get('transport_unit_id')
            if not unit_id:
                emit('error', {'message': 'Falta transport_unit_id'})
                return
            
            # Salir de sala específica de la unidad
            leave_room(f'unit_{unit_id}')
            
            # Remover suscriptor
            if unit_id in self.unit_subscribers:
                self.unit_subscribers[unit_id].discard(
                    self.socketio.server.environ.get('REMOTE_ADDR')
                )
            
            emit('unsubscription_response', {
                'status': 'unsubscribed',
                'transport_unit_id': unit_id,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('subscribe_to_all')
        def handle_subscribe_to_all():
            """Manejar suscripción a todos los eventos."""
            join_room('all_updates')
            emit('subscription_response', {
                'status': 'subscribed_to_all',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('unsubscribe_from_all')
        def handle_unsubscribe_from_all():
            """Manejar desuscripción de todos los eventos."""
            leave_room('all_updates')
            emit('unsubscription_response', {
                'status': 'unsubscribed_from_all',
                'timestamp': datetime.now().isoformat()
            })
    
    def broadcast_location_update(self, transport_unit_id: str, location: dict):
        """
        Transmitir actualización de ubicación a clientes suscritos.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            location: Datos de ubicación
        """
        event_data = {
            'type': 'location_update',
            'transport_unit_id': transport_unit_id,
            'location': location,
            'timestamp': datetime.now().isoformat()
        }
        
        # Transmitir a sala específica de la unidad
        self.socketio.emit(
            'location_update',
            event_data,
            room=f'unit_{transport_unit_id}'
        )
        
        # Transmitir a sala de todos los eventos
        self.socketio.emit(
            'update',
            event_data,
            room='all_updates'
        )
    
    def broadcast_state_change(
        self,
        transport_unit_id: str,
        new_state: str,
        old_state: str = None
    ):
        """
        Transmitir cambio de estado a clientes suscritos.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            new_state: Nuevo estado
            old_state: Estado anterior
        """
        event_data = {
            'type': 'state_change',
            'transport_unit_id': transport_unit_id,
            'new_state': new_state,
            'old_state': old_state,
            'timestamp': datetime.now().isoformat()
        }
        
        # Transmitir a sala específica de la unidad
        self.socketio.emit(
            'state_change',
            event_data,
            room=f'unit_{transport_unit_id}'
        )
        
        # Transmitir a sala de todos los eventos
        self.socketio.emit(
            'update',
            event_data,
            room='all_updates'
        )
    
    def broadcast_delay_detected(
        self,
        transport_unit_id: str,
        delay: dict
    ):
        """
        Transmitir evento de retraso detectado a clientes suscritos.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
            delay: Datos del retraso
        """
        event_data = {
            'type': 'delay_detected',
            'transport_unit_id': transport_unit_id,
            'delay': delay,
            'timestamp': datetime.now().isoformat()
        }
        
        # Transmitir a sala específica de la unidad
        self.socketio.emit(
            'delay_detected',
            event_data,
            room=f'unit_{transport_unit_id}'
        )
        
        # Transmitir a sala de todos los eventos
        self.socketio.emit(
            'update',
            event_data,
            room='all_updates'
        )
    
    def get_connected_clients_count(self) -> int:
        """
        Obtener cantidad de clientes conectados.
        
        Returns:
            Cantidad de clientes conectados
        """
        return len(self.socketio.server.environ.get('REMOTE_ADDR', []))
