# Telegram Video Clip Bot

Un bot de Telegram avanzado que procesa videos largos y genera clips aleatorios de 10 segundos con funcionalidades de spoiler y navegación interactiva.

## Características principales

- 🎬 **Procesamiento de videos largos** - Descarga y procesa videos automáticamente
- ✂️ **Generación de clips aleatorios** - Crea clips de 10 segundos desde puntos aleatorios
- 🎭 **Soporte de spoilers** - Los clips se envían con spoiler para sorpresa
- 🎮 **Navegación interactiva** - Botones para navegar entre clips
- 🐳 **Docker containerizado** - Fácil despliegue con Docker
- 📊 **Base de datos SQLite** - Almacenamiento persistente de datos
- 📝 **Logging completo** - Seguimiento detallado de operaciones

## Tecnologías utilizadas

- **Python 3.11+**
- **Telethon** - Cliente de Telegram
- **FFmpeg** - Procesamiento de video
- **SQLAlchemy** - ORM de base de datos
- **Docker & Docker Compose** - Containerización

## Instalación y uso

1. Clona el repositorio
2. Copia  a  y configura las variables
3. Ejecuta con Docker: `docker-compose up -d`

## Estructura del proyecto

- `src/` - Código fuente principal
- `src/handlers/` - Manejadores de eventos de Telegram
- `src/utils/` - Utilidades (FileManager para procesamiento de video)
- `src/database/` - Sistema de base de datos
- `tests/` - Tests del sistema

## Funcionalidades del bot

### Procesamiento de videos
- Detecta videos largos automáticamente
- Descarga con barra de progreso
- Genera múltiples clips aleatorios
- Envía clips con navegación interactiva

### Gestión de archivos
- Procesamiento seguro de archivos multimedia
- Limpieza automática de archivos temporales
- Soporte completo para videos MP4

### Interfaz de usuario
- Botones inline para navegación
- Mensajes con formato Markdown
- Soporte de spoilers para contenido sorpresa

---

⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub!
