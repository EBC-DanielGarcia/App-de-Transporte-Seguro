# Documentación de API - Sistema de Monitoreo de Transporte en Tiempo Real

## Descripción General

API REST para el Sistema Universitario de Monitoreo de Transporte en Tiempo Real. Proporciona endpoints para consultar unidades de transporte, rutas, historial y controlar simulaciones.

## Base URL

```
http://localhost:3001/api
```

## Autenticación

No se requiere autenticación para esta versión académica.

## Endpoints

### Health Check

#### GET /health
Verificar estado del servidor.

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "Sistema de Monitoreo de Transporte en Tiempo Real"
}
```

### Información de la Aplicación

#### GET /info
Obtener información de la aplicación.

**Respuesta:**
```json
{
  "name": "Sistema Universitario de Monitoreo de Transporte en Tiempo Real",
  "version": "1.0.0",
  "description": "Prototipo académico para visualizar ubicación, estado y tiempos estimados de transporte",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Unidades de Transporte

#### GET /transport-units
Obtener lista de todas las unidades de transporte.

**Query Parameters:**
- `state` (opcional): Filtrar por estado (En_Ruta, Detenido, Retraso, Fuera_Servicio)
- `sort` (opcional): Ordenar por (eta, state, name, distance)

**Ejemplo:**
```
GET /transport-units?state=En_Ruta&sort=eta
```

**Respuesta:**
```json
[
  {
    "id": "unit-1",
    "name": "Autobús 101",
    "route_id": "route-1",
    "state": "En_Ruta",
    "current_location": {
      "latitude": 19.4330,
      "longitude": -99.1300,
      "route_progress": 20.8
    },
    "speed": 40
  }
]
```

#### GET /transport-units/{id}
Obtener detalles completos de una unidad de transporte.

**Parámetros:**
- `id` (requerido): ID de la unidad

**Respuesta:**
```json
{
  "id": "unit-1",
  "name": "Autobús 101",
  "route_id": "route-1",
  "route_name": "Ruta Centro - Universidad",
  "current_location": {
    "latitude": 19.4330,
    "longitude": -99.1300,
    "route_progress": 20.8,
    "timestamp": "2024-01-15T10:30:00.000Z"
  },
  "state": "En_Ruta",
  "speed": 40,
  "current_stop": {
    "id": "stop-1-2",
    "name": "Estación Central",
    "distance_from_start": 3.5
  },
  "next_stop": {
    "id": "stop-1-3",
    "name": "Parque Metropolitano",
    "distance_from_start": 7.2,
    "eta": 12
  },
  "etas": {
    "stop-1-2": 2,
    "stop-1-3": 12,
    "stop-1-4": 25,
    "stop-1-5": 38
  },
  "history_count": 45,
  "metrics": {
    "total_travel_time": 120,
    "total_delay_time": 15,
    "delay_count": 2,
    "average_delay": 7.5,
    "on_time_percentage": 87.5
  },
  "created_at": "2024-01-15T08:00:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

#### GET /transport-units/{id}/history
Obtener historial de eventos de una unidad.

**Parámetros:**
- `id` (requerido): ID de la unidad

**Respuesta:**
```json
{
  "transport_unit_id": "unit-1",
  "events": [
    {
      "id": "event-1",
      "type": "STATE_CHANGE",
      "timestamp": "2024-01-15T08:00:00.000Z",
      "data": {
        "new_state": "En_Ruta",
        "old_state": "Detenido"
      }
    }
  ],
  "summary": {
    "transport_unit_id": "unit-1",
    "total_events": 45,
    "state_changes": 5,
    "delay_events": 2,
    "metrics": {
      "total_travel_time": 120,
      "total_delay_time": 15,
      "delay_count": 2,
      "average_delay": 7.5,
      "on_time_percentage": 87.5
    },
    "first_event": "2024-01-15T08:00:00.000Z",
    "last_event": "2024-01-15T10:30:00.000Z"
  }
}
```

### Rutas

#### GET /routes
Obtener lista de todas las rutas disponibles.

**Respuesta:**
```json
[
  {
    "id": "route-1",
    "name": "Ruta Centro - Universidad",
    "total_distance": 16.8,
    "estimated_duration": 45,
    "stops_count": 5
  }
]
```

#### GET /routes/{id}
Obtener detalles completos de una ruta.

**Parámetros:**
- `id` (requerido): ID de la ruta

**Respuesta:**
```json
{
  "id": "route-1",
  "name": "Ruta Centro - Universidad",
  "total_distance": 16.8,
  "estimated_duration": 45,
  "stops_count": 5,
  "stops": [
    {
      "id": "stop-1-1",
      "name": "Centro Histórico",
      "latitude": 19.4326,
      "longitude": -99.1332,
      "distance_from_start": 0,
      "estimated_stop_duration": 2
    }
  ]
}
```

#### GET /routes/{id}/stops
Obtener paradas de una ruta.

**Parámetros:**
- `id` (requerido): ID de la ruta

**Respuesta:**
```json
[
  {
    "id": "stop-1-1",
    "name": "Centro Histórico",
    "latitude": 19.4326,
    "longitude": -99.1332,
    "distance_from_start": 0,
    "estimated_stop_duration": 2
  }
]
```

### Simulación

#### POST /simulations/start
Iniciar simulación para una unidad de transporte.

**Body:**
```json
{
  "transport_unit_id": "unit-1",
  "route_id": "route-1",
  "name": "Autobús 101",
  "speed": 40
}
```

**Respuesta:**
```json
{
  "message": "Simulación iniciada",
  "transport_unit_id": "unit-1",
  "route_id": "route-1"
}
```

#### POST /simulations/stop
Detener simulación para una unidad de transporte.

**Body:**
```json
{
  "transport_unit_id": "unit-1"
}
```

**Respuesta:**
```json
{
  "message": "Simulación detenida",
  "transport_unit_id": "unit-1"
}
```

### Dashboard

#### GET /dashboard/summary
Obtener resumen del dashboard con estadísticas generales.

**Respuesta:**
```json
{
  "total_units": 5,
  "units_by_state": {
    "en_ruta": 3,
    "detenido": 1,
    "retraso": 1,
    "fuera_servicio": 0
  },
  "units_with_delays": 1,
  "average_delay_minutes": 15
}
```

## Códigos de Estado HTTP

- `200 OK`: Solicitud exitosa
- `400 Bad Request`: Parámetros inválidos
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

## Modelos de Datos

### TransportUnit
```json
{
  "id": "string",
  "name": "string",
  "route_id": "string",
  "current_location": {
    "latitude": "number",
    "longitude": "number",
    "route_progress": "number (0-100)",
    "timestamp": "ISO 8601 datetime"
  },
  "state": "En_Ruta | Detenido | Retraso | Fuera_Servicio",
  "speed": "number (km/h)",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

### Route
```json
{
  "id": "string",
  "name": "string",
  "stops": [
    {
      "id": "string",
      "name": "string",
      "latitude": "number",
      "longitude": "number",
      "distance_from_start": "number (km)",
      "estimated_stop_duration": "number (minutos)"
    }
  ],
  "total_distance": "number (km)",
  "estimated_duration": "number (minutos)"
}
```

### HistoryEvent
```json
{
  "id": "string",
  "transport_unit_id": "string",
  "type": "STATE_CHANGE | LOCATION_UPDATE | DELAY_DETECTED",
  "timestamp": "ISO 8601 datetime",
  "data": "object"
}
```

### Metrics
```json
{
  "transport_unit_id": "string",
  "total_travel_time": "number (minutos)",
  "total_delay_time": "number (minutos)",
  "delay_count": "number",
  "average_delay": "number (minutos)",
  "on_time_percentage": "number (0-100)"
}
```

## Ejemplos de Uso

### Obtener lista de unidades en ruta
```bash
curl -X GET "http://localhost:3001/api/transport-units?state=En_Ruta&sort=eta"
```

### Obtener detalles de una unidad
```bash
curl -X GET "http://localhost:3001/api/transport-units/unit-1"
```

### Iniciar simulación
```bash
curl -X POST "http://localhost:3001/api/simulations/start" \
  -H "Content-Type: application/json" \
  -d '{
    "transport_unit_id": "unit-1",
    "route_id": "route-1"
  }'
```

### Obtener historial de una unidad
```bash
curl -X GET "http://localhost:3001/api/transport-units/unit-1/history"
```

## Notas

- Todos los tiempos se devuelven en formato ISO 8601
- Las coordenadas geográficas están en formato decimal (WGS84)
- El progreso de la ruta se expresa como porcentaje (0-100)
- Los estados de transporte son: En_Ruta, Detenido, Retraso, Fuera_Servicio
