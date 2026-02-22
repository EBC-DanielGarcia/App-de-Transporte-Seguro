# App-de-Transporte-Seguro
Proyecto Final de la materia Hackaton tendencias en nuevas tecnologias.

# Sistema Universitario de Monitoreo de Transporte en Tiempo Real

## Descripción

Sistema académico que proporciona visibilidad completa de la ubicación, estado y tiempo estimado de llegada de unidades de transporte. El sistema simula la obtención de datos de ubicación, calcula tiempos estimados de llegada, detecta retrasos y presenta la información de forma visual clara e intuitiva.

## Características

- **Visualización de Ubicación en Tiempo Real**: Muestra la ubicación actual de las unidades de transporte en el recorrido
- **Estado del Transporte**: Indica si está en ruta, detenido, retrasado o fuera de servicio
- **Cálculo de Tiempos Estimados**: Calcula automáticamente el tiempo estimado de llegada a cada parada
- **Detección de Retrasos**: Detecta automáticamente cuando hay retrasos
- **Simulación de Datos**: Genera datos simulados de ubicación y estado para propósitos académicos
- **Historial de Eventos**: Mantiene un registro completo de cambios de estado y eventos
- **Persistencia de Datos**: Almacena datos para auditoría y análisis
- **Soporte Multi-Unidad**: Visualiza múltiples unidades de transporte simultáneamente

## Estructura del Proyecto

```
proyectos/sistema-seguimiento-procesos-tiempo-real/
├── backend/
│   ├── models/                 # Modelos de datos
│   │   ├── __init__.py
│   │   ├── transport_unit.py   # Unidad de transporte
│   │   ├── location.py         # Ubicación
│   │   ├── route.py            # Recorrido
│   │   ├── stop.py             # Parada
│   │   ├── transport_state.py  # Estado del transporte
│   │   ├── delay.py            # Retraso
│   │   ├── history_event.py    # Evento de historial
│   │   └── metrics.py          # Métricas
│   ├── services/               # Servicios de negocio
│   ├── utils/                  # Utilidades
│   ├── tests/                  # Tests
│   │   ├── __init__.py
│   │   └── test_models.py      # Tests de modelos
│   ├── main.py                 # Aplicación principal
│   ├── requirements.txt        # Dependencias
│   ├── pytest.ini              # Configuración de pytest
│   └── conftest.py             # Configuración compartida de tests
├── frontend/                   # Aplicación React (próximamente)
└── README.md                   # Este archivo
```

## Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## Instalación

### Backend

1. Navega al directorio del backend:
```bash
cd proyectos/sistema-seguimiento-procesos-tiempo-real/backend
```

2. Crea un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar la aplicación

```bash
python main.py
```

La aplicación estará disponible en `http://localhost:3001`

### Ejecutar los tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov

# Ejecutar tests específicos
pytest tests/test_models.py

# Ejecutar tests con salida detallada
pytest -v
```

## Modelos de Datos

### TransportUnit
Representa una unidad de transporte con su ubicación, estado y velocidad actual.

### Location
Coordenadas geográficas y progreso en el recorrido con timestamp.

### Route
Recorrido predefinido con sus paradas, distancia total y duración estimada.

### Stop
Parada específica en el recorrido con coordenadas y duración estimada de detención.

### TransportState
Estados posibles: En_Ruta, Detenido, Retraso, Fuera_Servicio

### Delay
Retraso detectado con magnitud en minutos y parada afectada.

### HistoryEvent
Evento registrado en el historial (cambio de estado, actualización de ubicación, retraso detectado).

### Metrics
Métricas de desempeño: tiempo total, retrasos acumulados, porcentaje de puntualidad.

## API Endpoints

### Health Check
- `GET /api/health` - Verifica el estado de la aplicación

### Info
- `GET /api/info` - Obtiene información de la aplicación

## Desarrollo

### Agregar nuevos modelos

1. Crea un archivo en `backend/models/`
2. Define la clase con `@dataclass`
3. Implementa métodos `to_dict()` y `from_dict()`
4. Actualiza `backend/models/__init__.py`
5. Agrega tests en `backend/tests/test_models.py`

### Agregar nuevos servicios

1. Crea un archivo en `backend/services/`
2. Implementa la lógica de negocio
3. Agrega tests en `backend/tests/`

## Testing

El proyecto utiliza:
- **pytest**: Framework de testing
- **pytest-cov**: Cobertura de código
- **hypothesis**: Property-based testing

### Estructura de tests

- Tests unitarios: Verifican ejemplos específicos y casos límite
- Tests de propiedad: Verifican propiedades universales
- Tests de integración: Verifican que componentes trabajen juntos

## Requisitos del Sistema

El sistema implementa los siguientes requisitos:

1. **Visualización de Ubicación en Tiempo Real** (Req 1)
2. **Visualización del Estado del Transporte** (Req 2)
3. **Cálculo y Visualización de Tiempos Estimados** (Req 3)
4. **Detección de Retrasos** (Req 4)
5. **Simulación de Datos de Ubicación** (Req 5)
6. **Visualización del Recorrido** (Req 6)
7. **Interfaz Visual Intuitiva** (Req 7)
8. **Historial de Eventos** (Req 8)
9. **Persistencia de Datos** (Req 9)
10. **Soporte para Múltiples Unidades** (Req 10)

## Licencia

Proyecto académico - Universidad

## Autores

Sistema desarrollado como prototipo académico para el monitoreo de transporte en tiempo real.
