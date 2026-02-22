# Motor de Simulación - Documentación

## Descripción General

El motor de simulación proporciona la capacidad de simular el movimiento realista de unidades de transporte a lo largo de recorridos predefinidos. Incluye dos componentes principales:

1. **SimulationEngine**: Motor de simulación que genera y actualiza ubicaciones
2. **SimulationScheduler**: Scheduler que actualiza periódicamente múltiples unidades

## Componentes

### SimulationEngine

Ubicación: `services/simulation_engine.py`

#### Responsabilidades

- Generar ubicaciones iniciales aleatorias en el recorrido
- Actualizar ubicaciones con movimiento realista
- Simular detenciones en paradas
- Simular retrasos ocasionales
- Gestionar múltiples simulaciones independientes

#### Métodos Principales

```python
def start_simulation(transport_unit: TransportUnit, route: Route) -> None
    """Inicia la simulación de una unidad de transporte."""

def stop_simulation(transport_unit_id: str) -> None
    """Detiene la simulación de una unidad."""

def update_location(transport_unit_id: str) -> Optional[Location]
    """Actualiza la ubicación de una unidad."""

def get_current_state(transport_unit_id: str) -> Optional[Dict]
    """Obtiene el estado actual de una simulación."""

def is_running(transport_unit_id: str) -> bool
    """Verifica si una unidad está en simulación."""
```

#### Características de Simulación

- **Velocidad Variable**: 30-60 km/h (configurable)
- **Detenciones en Paradas**: 30-120 segundos (configurable)
- **Retrasos Ocasionales**: 15% de probabilidad, 5-20 minutos (configurable)
- **Movimiento Continuo**: Sin saltos entre ubicaciones
- **Interpolación de Coordenadas**: Movimiento suave entre paradas

#### Ejemplo de Uso

```python
from services.simulation_engine import SimulationEngine
from models import TransportUnit, Route

# Crear motor
engine = SimulationEngine()

# Iniciar simulación
engine.start_simulation(transport_unit, route)

# Actualizar ubicación
new_location = engine.update_location(transport_unit.id)

# Obtener estado
state = engine.get_current_state(transport_unit.id)

# Detener simulación
engine.stop_simulation(transport_unit.id)
```

### SimulationScheduler

Ubicación: `services/simulation_scheduler.py`

#### Responsabilidades

- Actualizar periódicamente múltiples unidades
- Gestionar callbacks de actualización
- Proporcionar thread-safety
- Controlar el ciclo de vida del scheduler

#### Métodos Principales

```python
def start_scheduler() -> None
    """Inicia el scheduler de actualización periódica."""

def stop_scheduler() -> None
    """Detiene el scheduler."""

def add_transport_unit(transport_unit: TransportUnit, route: Route) -> None
    """Añade una unidad para simular."""

def remove_transport_unit(transport_unit_id: str) -> None
    """Remueve una unidad de la simulación."""

def register_update_callback(callback: Callable) -> None
    """Registra un callback para actualizaciones."""

def unregister_update_callback(callback: Callable) -> None
    """Desregistra un callback."""

def get_active_units() -> List[str]
    """Obtiene lista de unidades activas."""

def is_scheduler_running() -> bool
    """Verifica si el scheduler está corriendo."""
```

#### Características

- **Actualización Periódica**: Cada segundo (configurable)
- **Thread-Safe**: Usa locks para operaciones concurrentes
- **Callbacks**: Sistema de callbacks para reaccionar a actualizaciones
- **Múltiples Unidades**: Maneja múltiples unidades simultáneamente

#### Ejemplo de Uso

```python
from services.simulation_scheduler import SimulationScheduler

# Crear scheduler
scheduler = SimulationScheduler(update_interval=1.0)

# Registrar callback
def on_location_update(unit_id, location):
    print(f"Unit {unit_id} updated to {location}")

scheduler.register_update_callback(on_location_update)

# Agregar unidades
scheduler.add_transport_unit(unit1, route1)
scheduler.add_transport_unit(unit2, route2)

# Iniciar scheduler
scheduler.start_scheduler()

# ... hacer algo ...

# Detener scheduler
scheduler.stop_scheduler()
```

## Requisitos Validados

### Requisito 5.1: Generación de Datos Simulados
- ✅ El sistema genera ubicaciones iniciales aleatorias
- ✅ Las ubicaciones están dentro del recorrido (0-100% de progreso)
- ✅ Se generan coordenadas válidas interpoladas

### Requisito 5.2: Actualización Periódica
- ✅ Las ubicaciones se actualizan cada segundo (configurable)
- ✅ No hay gaps en las actualizaciones
- ✅ Los intervalos son regulares

### Requisito 5.3: Movimiento Realista
- ✅ El movimiento es continuo sin saltos
- ✅ La velocidad está entre 30-60 km/h
- ✅ El progreso es monótonamente creciente
- ✅ Las coordenadas se interpolan suavemente

### Requisito 5.4: Detenciones en Paradas
- ✅ Se detectan las paradas automáticamente
- ✅ La ubicación se mantiene constante durante la detención
- ✅ La duración es variable (30-120 segundos)

## Tests

### Test Suite

- **test_simulation_engine.py**: 22 tests para SimulationEngine
- **test_simulation_scheduler.py**: 22 tests para SimulationScheduler
- **Total**: 44 tests, todos pasando

### Cobertura

- SimulationEngine: 82% de cobertura
- SimulationScheduler: 91% de cobertura

### Categorías de Tests

#### SimulationEngine
1. **Inicialización**: Crear, iniciar, detener simulaciones
2. **Generación de Ubicaciones**: Ubicaciones iniciales válidas
3. **Movimiento**: Actualización continua y realista
4. **Detenciones**: Detección y manejo de paradas
5. **Estado**: Obtener estado actual
6. **Múltiples Unidades**: Independencia entre simulaciones
7. **Reinicio**: Reiniciar simulaciones

#### SimulationScheduler
1. **Inicialización**: Crear scheduler con configuración
2. **Control**: Iniciar y detener scheduler
3. **Unidades**: Agregar y remover unidades
4. **Callbacks**: Registrar y ejecutar callbacks
5. **Actualizaciones Periódicas**: Verificar intervalos regulares
6. **Múltiples Unidades**: Actualizar múltiples unidades
7. **Thread-Safety**: Operaciones concurrentes seguras

## Configuración

### SimulationEngine

```python
# Velocidad (km/h)
_min_speed = 30
_max_speed = 60

# Detenciones en paradas (segundos)
_min_stop_duration = 30
_max_stop_duration = 120

# Retrasos
_delay_probability = 0.15  # 15%
_delay_min = 5  # minutos
_delay_max = 20  # minutos
```

### SimulationScheduler

```python
# Intervalo de actualización (segundos)
update_interval = 1.0
```

## Integración con Otros Componentes

### Con PersistenceService

```python
from services.simulation_scheduler import SimulationScheduler
from services.persistence_service import PersistenceService

scheduler = SimulationScheduler()
persistence = PersistenceService()

def save_location(unit_id, location):
    persistence.save_location_update(unit_id, location)

scheduler.register_update_callback(save_location)
```

### Con TransportState

El motor actualiza automáticamente el estado del transporte:
- `EN_RUTA`: Cuando se está moviendo
- `DETENIDO`: Cuando está en una parada
- `RETRASO`: Cuando hay retrasos (a implementar en motor de detección)

## Notas de Implementación

### Interpolación de Coordenadas

Las coordenadas se interpolan linealmente entre paradas basadas en el progreso del recorrido:

```
progress_per_stop = 100 / (num_stops - 1)
stop_index = int(progress / progress_per_stop)
progress_in_segment = (progress % progress_per_stop) / progress_per_stop
new_lat = stop1.lat + (stop2.lat - stop1.lat) * progress_in_segment
new_lon = stop1.lon + (stop2.lon - stop1.lon) * progress_in_segment
```

### Thread-Safety

El SimulationScheduler usa `threading.Lock` para proteger:
- Acceso a `_transport_units`
- Acceso a `_update_callbacks`
- Cambios de estado del scheduler

### Manejo de Errores

- Los callbacks que lanzan excepciones no detienen el scheduler
- Las excepciones se registran pero se continúa con el loop
- El scheduler es resiliente a errores

## Próximos Pasos

1. **Integración con ETA Calculator**: Calcular tiempos estimados basados en ubicación
2. **Integración con Delay Detection**: Detectar retrasos automáticamente
3. **Integración con Persistence**: Guardar ubicaciones y cambios de estado
4. **API REST**: Exponer endpoints para controlar simulaciones
5. **WebSocket**: Transmitir actualizaciones en tiempo real al frontend

## Troubleshooting

### La simulación no se actualiza

- Verificar que `start_scheduler()` fue llamado
- Verificar que `add_transport_unit()` fue llamado
- Verificar que el scheduler está corriendo: `is_scheduler_running()`

### Las ubicaciones no cambian

- Verificar que `update_location()` está siendo llamado
- Verificar que hay tiempo transcurrido entre actualizaciones
- Verificar que la unidad no está detenida en una parada

### Los callbacks no se ejecutan

- Verificar que `register_update_callback()` fue llamado
- Verificar que el callback no lanza excepciones
- Verificar que el scheduler está corriendo

## Referencias

- Requisitos: `requirements.md` (Requisito 5)
- Diseño: `design.md` (Properties 9-12)
- Tests: `tests/test_simulation_engine.py`, `tests/test_simulation_scheduler.py`
