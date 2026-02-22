"""
Servicio de actualización periódica de simulaciones.

Este servicio proporciona:
- Actualización periódica de ubicaciones (cada segundo)
- Manejo de múltiples unidades simultáneamente
- Control de inicio y parada del scheduler
"""

import threading
import time
from typing import Dict, Optional, Callable, List
from models import TransportUnit, Route
from .simulation_engine import SimulationEngine


class SimulationScheduler:
    """
    Scheduler para actualizar periódicamente las simulaciones de transporte.
    
    Actualiza la ubicación de todas las unidades en simulación cada segundo.
    """
    
    def __init__(self, simulation_engine: Optional[SimulationEngine] = None, 
                 update_interval: float = 1.0):
        """
        Inicializa el scheduler de simulación.
        
        Args:
            simulation_engine: Motor de simulación a usar (crea uno nuevo si no se proporciona)
            update_interval: Intervalo de actualización en segundos (default: 1.0)
        """
        self._simulation_engine = simulation_engine or SimulationEngine()
        self._update_interval = update_interval
        
        # Control del scheduler
        self._is_running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Unidades a simular: {transport_unit_id: (TransportUnit, Route)}
        self._transport_units: Dict[str, tuple] = {}
        
        # Callbacks para eventos de actualización
        self._update_callbacks: List[Callable] = []
    
    def start_scheduler(self) -> None:
        """Inicia el scheduler de actualización periódica."""
        with self._lock:
            if self._is_running:
                return
            
            self._is_running = True
            self._scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                daemon=True
            )
            self._scheduler_thread.start()
    
    def stop_scheduler(self) -> None:
        """Detiene el scheduler de actualización periódica."""
        with self._lock:
            self._is_running = False
        
        # Esperar a que el thread termine
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)
            self._scheduler_thread = None
    
    def add_transport_unit(self, transport_unit: TransportUnit, route: Route) -> None:
        """
        Añade una unidad de transporte para simular.
        
        Args:
            transport_unit: Unidad de transporte a simular
            route: Recorrido que debe seguir
        """
        with self._lock:
            self._transport_units[transport_unit.id] = (transport_unit, route)
            
            # Iniciar simulación en el motor
            self._simulation_engine.start_simulation(transport_unit, route)
    
    def remove_transport_unit(self, transport_unit_id: str) -> None:
        """
        Remueve una unidad de transporte de la simulación.
        
        Args:
            transport_unit_id: ID de la unidad de transporte
        """
        with self._lock:
            if transport_unit_id in self._transport_units:
                del self._transport_units[transport_unit_id]
                
                # Detener simulación en el motor
                self._simulation_engine.stop_simulation(transport_unit_id)
    
    def register_update_callback(self, callback: Callable) -> None:
        """
        Registra un callback para ser llamado cuando se actualiza una ubicación.
        
        Args:
            callback: Función a llamar con (transport_unit_id, new_location)
        """
        with self._lock:
            self._update_callbacks.append(callback)
    
    def unregister_update_callback(self, callback: Callable) -> None:
        """
        Desregistra un callback de actualización.
        
        Args:
            callback: Función a desregistrar
        """
        with self._lock:
            if callback in self._update_callbacks:
                self._update_callbacks.remove(callback)
    
    def get_active_units(self) -> List[str]:
        """
        Obtiene la lista de IDs de unidades activas en simulación.
        
        Returns:
            Lista de IDs de unidades en simulación
        """
        with self._lock:
            return list(self._transport_units.keys())
    
    def is_scheduler_running(self) -> bool:
        """
        Verifica si el scheduler está en ejecución.
        
        Returns:
            True si el scheduler está corriendo, False en caso contrario
        """
        return self._is_running
    
    def _scheduler_loop(self) -> None:
        """
        Loop principal del scheduler que actualiza periódicamente las ubicaciones.
        """
        while self._is_running:
            try:
                # Obtener lista de unidades a actualizar
                with self._lock:
                    units_to_update = list(self._transport_units.keys())
                
                # Actualizar cada unidad
                for unit_id in units_to_update:
                    if not self._is_running:
                        break
                    
                    # Actualizar ubicación
                    new_location = self._simulation_engine.update_location(unit_id)
                    
                    if new_location:
                        # Llamar callbacks
                        with self._lock:
                            callbacks = list(self._update_callbacks)
                        
                        for callback in callbacks:
                            try:
                                callback(unit_id, new_location)
                            except Exception as e:
                                # Log error pero continuar
                                print(f"Error en callback de actualización: {e}")
                
                # Esperar hasta la próxima actualización
                time.sleep(self._update_interval)
            
            except Exception as e:
                # Log error pero continuar el loop
                print(f"Error en scheduler loop: {e}")
                time.sleep(self._update_interval)
