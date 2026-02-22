# Sistema de Monitoreo de Transporte en Tiempo Real
## Guía de Instalación para Mac

---

## 🚀 Instalación Rápida (5 minutos)

### Paso 1: Preparar el Entorno

```bash
# Abre Terminal y navega a la carpeta del proyecto
cd /ruta/a/sistema-seguimiento-procesos-tiempo-real
```

### Paso 2: Instalar Backend

```bash
# Abre Terminal 1
cd backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python main.py

# Deberías ver: "Running on http://127.0.0.1:3001"
```

### Paso 3: Instalar Frontend

```bash
# Abre Terminal 2 (Cmd + T)
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor
npm start

# Deberías ver: "Compiled successfully!"
```

### Paso 4: Acceder a la Aplicación

```
Abre tu navegador en: http://localhost:3000
```

---

## ✅ Verificación

Si ves esto, ¡todo está funcionando!

- ✅ Lista de 5 autobuses
- ✅ Estados de cada autobús (En Ruta, Detenido, Retraso)
- ✅ Filtros y opciones de ordenamiento
- ✅ Interfaz completa y funcional

---

## 📚 Documentación Disponible

| Documento | Descripción |
|-----------|-------------|
| `INSTALLATION_MAC.md` | Guía completa de instalación paso a paso |
| `QUICK_START.md` | Inicio rápido con ejemplos |
| `TESTING_GUIDE.md` | Guía completa de pruebas |
| `API_DOCUMENTATION.md` | Documentación de todos los endpoints |
| `COMPONENTS_DOCUMENTATION.md` | Documentación de componentes React |
| `DOCUMENTACION_COMPLETA.md` | Documentación consolidada |
| `IMPLEMENTATION_SUMMARY.md` | Resumen técnico de implementación |

---

## 🔧 Requisitos Previos

Antes de instalar, verifica que tengas:

```bash
# Python 3.8 o superior
python3 --version

# Node.js y npm
node --version
npm --version
```

Si no los tienes, instala con Homebrew:

```bash
brew install python3
brew install node
```

---

## 🎯 Características Principales

✅ **Visualización en Tiempo Real**
- Ubicación actual de cada unidad
- Estado con indicadores visuales
- ETA para cada parada

✅ **Filtrado y Ordenamiento**
- Filtrar por estado (En Ruta, Detenido, Retraso)
- Ordenar por ETA, estado, nombre, distancia

✅ **Detalles Completos**
- Información de ubicación
- Recorrido visual con paradas
- Métricas de desempeño
- Historial de eventos

✅ **Diseño Responsive**
- Funciona en desktop, tablet y mobile
- Sin scroll horizontal en mobile

---

## 📊 Datos de Ejemplo

El sistema viene precargado con:

- **3 Rutas**: Centro-Universidad, Aeropuerto-Centro, Residencial-Centro
- **5 Autobuses**: 101, 202, 303, 404, 505
- **Estados**: En Ruta, Detenido, Retraso

---

## 🐛 Solución de Problemas

### "command not found: python3"
```bash
brew install python3
```

### "command not found: npm"
```bash
brew install node
```

### "Port 3001 is already in use"
```bash
lsof -i :3001
kill -9 PID
```

### "Port 3000 is already in use"
```bash
lsof -i :3000
kill -9 PID
```

### El frontend no carga datos
```bash
# Verifica que el backend esté corriendo
curl http://localhost:3001/api/health
```

---

## 📱 Pruebas Rápidas

### 1. Ver Lista de Unidades
```
http://localhost:3000
```

### 2. Filtrar por Estado
- Selecciona "En Ruta" en el dropdown
- Deberían aparecer 3 unidades

### 3. Ver Detalles
- Haz clic en "Autobús 101"
- Navega entre las pestañas

### 4. Probar API
```bash
curl http://localhost:3001/api/transport-units
```

---

## 🔄 Comandos Útiles

### Reiniciar Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

### Reiniciar Frontend
```bash
cd frontend
npm start
```

### Detener Servidores
```bash
# En cada terminal, presiona:
Ctrl + C
```

### Desactivar Entorno Virtual
```bash
deactivate
```

---

## 📁 Estructura del Proyecto

```
sistema-seguimiento-procesos-tiempo-real/
├── backend/
│   ├── venv/                    # Entorno virtual
│   ├── models/                  # Modelos de datos
│   ├── services/                # Servicios
│   ├── tests/                   # Pruebas
│   ├── main.py                  # Aplicación principal
│   ├── requirements.txt          # Dependencias Python
│   └── seed_data.py             # Datos de ejemplo
│
├── frontend/
│   ├── node_modules/            # Dependencias Node
│   ├── public/                  # Archivos estáticos
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   ├── App.js               # Componente principal
│   │   └── App.css              # Estilos
│   ├── package.json             # Dependencias Node
│   └── package-lock.json        # Lock file
│
└── Documentación/
    ├── INSTALLATION_MAC.md
    ├── QUICK_START.md
    ├── TESTING_GUIDE.md
    ├── API_DOCUMENTATION.md
    ├── COMPONENTS_DOCUMENTATION.md
    ├── DOCUMENTACION_COMPLETA.md
    └── IMPLEMENTATION_SUMMARY.md
```

---

## 🎓 Próximos Pasos

1. **Instala siguiendo los pasos arriba**
2. **Abre http://localhost:3000**
3. **Explora la interfaz**
4. **Lee la documentación adicional**
5. **Prueba los endpoints de API**

---

## 📞 Soporte

Si tienes problemas:

1. Consulta `INSTALLATION_MAC.md` para solución de problemas
2. Revisa los logs en las terminales
3. Verifica que los puertos 3000 y 3001 estén disponibles
4. Asegúrate de que Python 3.8+ y Node.js estén instalados

---

## ✨ ¡Listo!

Tu sistema está listo para instalar. Sigue los pasos de instalación rápida arriba y disfruta del sistema.

**¡Bienvenido al Sistema de Monitoreo de Transporte en Tiempo Real!**

---

## 📄 Documentación Completa

Para más detalles, consulta:
- `INSTALLATION_MAC.md` - Instalación paso a paso
- `DOCUMENTACION_COMPLETA.md` - Documentación consolidada
- `API_DOCUMENTATION.md` - Documentación de API
- `TESTING_GUIDE.md` - Guía de pruebas

---

**Última actualización**: Febrero 2026
**Versión**: 1.0.0
**Estado**: ✅ Completamente Funcional
