# pequeno Bot - Bot de Telegram Modular con Telethon

Bot de Telegram modular desarrollado con Telethon que incluye un sistema completo de gestión de base de datos, cliente de mensajería centralizado y arquitectura escalable.

## 🚀 Características Principales

- **🔧 Configuración Centralizada**: Sistema de configuración basado en variables de entorno
- **💾 Base de Datos Completa**: SQLite con modelos y gestión automática de mensajes
- **📨 Cliente de Mensajería**: Sistema centralizado para todas las interacciones con Telegram
- **🎛️ Handlers Modulares**: Separación clara entre comandos y eventos
- **📊 Sistema de Estadísticas**: Análisis completo de actividad del bot
- **🔍 Logging Avanzado**: Sistema de logs configurable y detallado
- **🐳 Docker Ready**: Contenedorización completa con docker-compose
- **🔐 Gestión de Respuestas**: Sistema inteligente de respuesta a mensajes

## 🏗️ Arquitectura del Proyecto

```
pequeno_bot/
├── main.py                    # 🚀 Punto de entrada del bot
├── requirements.txt           # 📦 Dependencias Python
├── Dockerfile                 # 🐳 Configuración Docker
├── docker-compose.yml         # 🐳 Orquestación de contenedores
├── .env.example              # 📝 Ejemplo de configuración
├── setup.sh                  # 🛠️ Script de configuración automática
│
├── src/                      # 📁 Código fuente principal
│   ├── config/              # ⚙️ Sistema de configuración
│   │   ├── __init__.py      # Exportaciones del módulo
│   │   ├── bot_config.py    # Clase de configuración principal
│   │   └── logger.py        # Sistema de logging configurado
│   │
│   ├── database/            # � Sistema de base de datos
│   │   ├── __init__.py      # Exportaciones del módulo
│   │   ├── models.py        # Modelos SQLAlchemy (Message, User, Chat)
│   │   └── manager.py       # Gestor de base de datos y estadísticas
│   │
│   ├── handlers/            # 🎛️ Manejadores de eventos
│   │   ├── __init__.py      # Exportaciones del módulo
│   │   ├── event_handler.py # Procesamiento de mensajes entrantes
│   │   └── command_handler.py # Comandos del bot (/start, /stats, etc.)
│   │
│   ├── utils/               # �️ Utilidades
│   │   └── __init__.py      # Exportaciones del módulo
│   │
│   └── telegram_client.py   # � Cliente de mensajería centralizado
│
├── data/                    # 💾 Datos persistentes (creado automáticamente)
│   └── bot_data.db         # Base de datos SQLite
├── logs/                    # 📋 Archivos de log (creado automáticamente)
│   └── bot.log             # Log principal del bot
└── downloads/               # 📁 Descargas temporales (creado automáticamente)
```

## 🎯 Módulos Implementados

### 1. 🔧 Sistema de Configuración (`src/config/`)

**Clase BotConfig** - Gestión centralizada de todas las configuraciones:
- ✅ Validación automática de variables de entorno obligatorias
- ✅ Valores por defecto para configuraciones opcionales  
- ✅ Conversión automática de tipos (string → int, bool, etc.)
- ✅ Métodos de validación y información detallada
- ✅ Soporte para configuración de chats objetivo

**Logger Configurado** - Sistema de logging avanzado:
- ✅ Configuración centralizada en `src/config/logger.py`
- ✅ Niveles configurables (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Rotación automática de archivos de log
- ✅ Formato consistente con timestamps y niveles

### 2. 💾 Sistema de Base de Datos (`src/database/`)

**Modelos SQLAlchemy** (`models.py`):
- **Message**: Almacena todos los mensajes con metadata completa
- **User**: Información de usuarios con estadísticas
- **Chat**: Información de chats y grupos

**Gestor de Base de Datos** (`manager.py`):
- ✅ Inicialización automática de tablas
- ✅ Procesamiento automático de eventos de Telethon
- ✅ Estadísticas avanzadas (mensajes por tipo, top chats, actividad)
- ✅ Métodos de consulta optimizados
- ✅ Gestión automática de sesiones

### 3. 📨 Cliente de Mensajería (`telegram_client.py`)

**TelegramMessenger** - Interface centralizada para Telegram:
- ✅ **Envío de mensajes**: Texto con formato Markdown/HTML
- ✅ **Edición de mensajes**: Modificación de mensajes existentes
- ✅ **Envío de multimedia**: Fotos, videos, animaciones, stickers
- ✅ **Álbumes de medios**: Envío de múltiples archivos agrupados
- ✅ **Documentos**: Envío de archivos de cualquier tipo
- ✅ **Respuestas inteligentes**: Sistema automático de reply_to_message
- ✅ **Notificaciones**: Envío a chat personal configurado
- ✅ **Manejo de errores**: FloodWait automático, reintentos
- ✅ **Logging detallado**: Seguimiento de todas las operaciones

### 4. 🎛️ Handlers Modulares (`src/handlers/`)

**EventHandler** (`event_handler.py`):
- ✅ Procesamiento de todos los mensajes entrantes
- ✅ Almacenamiento automático en base de datos
- ✅ Logging detallado de actividad
- ✅ Soporte para mensajes editados

**CommandHandler** (`command_handler.py`):
- ✅ **`/start`** - Inicialización del bot
- ✅ **`/ping`** - Verificación de estado
- ✅ **`/help`** - Ayuda completa con comandos
- ✅ **`/status`** - Estado del bot e información
- ✅ **`/stats`** - Estadísticas detalladas de la base de datos
- ✅ **`/test_messenger`** - Pruebas del cliente de mensajería
- ✅ **`/send_test`** - Envío de mensajes de prueba
- ✅ **`/send_notification`** - Notificaciones personales

Todos los comandos utilizan el sistema de respuestas inteligentes del `TelegramMessenger`.

## ⚙️ Configuración Completa

### Variables de Entorno Obligatorias

```env
# 🔑 Credenciales de Telegram API (https://my.telegram.org/auth)
API_ID=tu_api_id
API_HASH=tu_api_hash
BOT_TOKEN=tu_bot_token
```

### Variables de Entorno Opcionales

```env
# 🎯 Configuración de Chats
CHAT_TARGET=-1001234567890    # Chat objetivo para mensajes
CHAT_ME=123456789            # Chat personal para notificaciones

# 💾 Base de Datos
DATABASE_URL=sqlite:///data/bot_data.db

# 📋 Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# 📁 Directorios
DATA_DIR=data
LOGS_DIR=logs
DOWNLOADS_DIR=downloads

# ⚙️ Configuración General
DEBUG_MODE=false
```

## 🚀 Instalación y Despliegue

### Método 1: Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone <tu-repositorio>
cd pequeno_bot

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Ejecutar con Docker Compose
docker-compose up -d

# 4. Ver logs
docker-compose logs -f pequeno_bot
```

### Método 2: Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 4. Ejecutar setup automático
chmod +x setup.sh
./setup.sh

# 5. Ejecutar el bot
python main.py
```

## 🔧 Características de la Configuración

### Clase BotConfig

La nueva clase `BotConfig` en `src/config/bot_config.py` proporciona:

- ✅ **Validación automática** de variables de entorno
- ✅ **Valores por defecto** para configuraciones opcionales
- ✅ **Conversión de tipos** automática
- ✅ **Propiedades útiles** como `is_group_restricted`
- ✅ **Métodos de información** como `get_group_info()`

### Ejemplo de Uso

```python
from src.config import BotConfig

# Crear configuración
config = BotConfig()

# Acceder a valores
print(f"API ID: {config.api_id}")
print(f"Bot Token: {config.bot_token}")

# Verificar restricciones
if config.is_group_restricted:
    print("Bot restringido a grupo específico")
else:
    print("Bot funcionará en todos los grupos")

# Obtener información
print(config.get_group_info())
```

## 📊 Variables de Configuración Disponibles

### Obligatorias
- `API_ID` - ID de la aplicación de Telegram
- `API_HASH` - Hash de la aplicación de Telegram  
- `BOT_TOKEN` - Token del bot

### Grupo Objetivo
- `TARGET_GROUP_ID` - ID del grupo específico
- `TARGET_GROUP_USERNAME` - Username del grupo específico

### Base de Datos
- `DATABASE_URL` - URL de conexión a la base de datos

### Logging
- `LOG_LEVEL` - Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE` - Archivo de log

### Directorios
- `DOWNLOADS_DIR` - Directorio de descargas
- `TEMP_DIR` - Directorio temporal
- `DATA_DIR` - Directorio de datos
- `LOGS_DIR` - Directorio de logs

### Procesamiento
- `MAX_FILE_SIZE_MB` - Tamaño máximo de archivo en MB
- `VIDEO_QUALITY` - Calidad de video (low, medium, high)
- `IMAGE_QUALITY` - Calidad de imagen (0-100)

### Notificaciones
- `ENABLE_NOTIFICATIONS` - Habilitar notificaciones
- `NOTIFICATION_CHAT_ID` - Chat ID para notificaciones

### Rate Limiting
- `RATE_LIMIT_MESSAGES` - Máximo mensajes por ventana
- `RATE_LIMIT_WINDOW` - Ventana de tiempo en segundos

### Desarrollo
- `DEBUG_MODE` - Modo debug
- `DEV_MODE` - Modo desarrollo

## 🛠️ Desarrollo

### Añadir Nueva Configuración

1. **Agregar variable al archivo `.env.example`**
2. **Actualizar la clase `BotConfig`**:

```python
# En src/config/bot_config.py
def __init__(self):
    # ... otras configuraciones ...
    self.mi_nueva_config = os.getenv('MI_NUEVA_CONFIG', 'valor_por_defecto')
```

3. **Usar en el código**:

```python
# En cualquier parte del código
from src.config import BotConfig

config = BotConfig()
valor = config.mi_nueva_config
```

### Validación Personalizada

```python
def _validate_config(self):
    # ... validaciones existentes ...
    
    # Nueva validación
    if self.mi_nueva_config not in ['opcion1', 'opcion2']:
        raise ValueError("MI_NUEVA_CONFIG debe ser 'opcion1' o 'opcion2'")
```

## 🐛 Solución de Problemas

### Error: "Variable de entorno requerida no encontrada"

1. Verifica que el archivo `.env` existe
2. Asegúrate de que la variable está definida sin espacios
3. Ejecuta `python config_setup.py check` para validar

### Error: "Error al convertir variable"

1. Verifica que el valor sea del tipo correcto (número para IDs)
2. Asegúrate de que no hay espacios extra en el valor

### El bot no encuentra la configuración

1. Verifica que estás ejecutando desde el directorio correcto
2. Asegúrate de que `src/config/__init__.py` existe

## 📝 TODO

- [ ] Añadir configuración para webhooks
- [ ] Implementar configuración de proxy
- [ ] Añadir configuración de idioma
- [ ] Crear configuración para plugins
- [ ] Implementar configuración de backup

---

**¡Configuración modular y escalable! 🎛️✨**