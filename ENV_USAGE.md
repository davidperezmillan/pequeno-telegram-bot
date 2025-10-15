# Variables de Entorno en pequeno_bot

## 📍 **Dónde se utilizan las variables de entorno**

### 🔧 **Archivo Principal: `src/config/bot_config.py`**

Todas las variables de entorno se cargan y utilizan en la clase `BotConfig`:

#### Variables Obligatorias (Credenciales):
```python
# Credenciales de Telegram API
self.api_id = self._get_required_env('API_ID', int)          # → API_ID
self.api_hash = self._get_required_env('API_HASH')          # → API_HASH  
self.bot_token = self._get_required_env('BOT_TOKEN')        # → BOT_TOKEN
```
**Usado en**: `main.py` → `TelegramClient('pequeno_bot_session', self.config.api_id, self.config.api_hash)`

#### Variables Opcionales (Configuración de Grupo):
```python
# Configuración del grupo objetivo
self.target_group_id = self._get_optional_env('TARGET_GROUP_ID', int)      # → TARGET_GROUP_ID
self.target_group_username = self._get_optional_env('TARGET_GROUP_USERNAME') # → TARGET_GROUP_USERNAME
```
**Usado en**: `src/handlers/command_handler.py` → comando `/status` para mostrar configuración del grupo

#### Variables de Base de Datos:
```python
self.database_url = os.getenv('DATABASE_URL', 'sqlite:///data/bot_data.db')  # → DATABASE_URL
```
**Usado en**: `src/database/manager.py` → inicialización de SQLite

#### Variables de Directorios:
```python
self.temp_dir = os.getenv('TEMP_DIR', 'temp')             # → TEMP_DIR
self.data_dir = os.getenv('DATA_DIR', 'data')             # → DATA_DIR
self.logs_dir = os.getenv('LOGS_DIR', 'logs')             # → LOGS_DIR
self.downloads_dir = os.getenv('DOWNLOADS_DIR', 'downloads') # → DOWNLOADS_DIR
```
**Usado en**: Todo el sistema para crear directorios necesarios

#### Variables de Logging:
```python
self.log_level = os.getenv('LOG_LEVEL', 'INFO')           # → LOG_LEVEL
self.log_file = os.getenv('LOG_FILE', 'logs/bot.log')     # → LOG_FILE
```
**Usado en**: `src/utils/logger.py` → configuración del sistema de logging

#### Variables de Procesamiento:
```python
self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '50'))      # → MAX_FILE_SIZE_MB
self.video_quality = os.getenv('VIDEO_QUALITY', 'medium')            # → VIDEO_QUALITY
self.image_quality = int(os.getenv('IMAGE_QUALITY', '85'))           # → IMAGE_QUALITY
```
**Preparado para**: Futuras funcionalidades de procesamiento de archivos

#### Variables de Notificaciones:
```python
self.enable_notifications = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'  # → ENABLE_NOTIFICATIONS
self.notification_chat_id = self._get_optional_env('NOTIFICATION_CHAT_ID', int)          # → NOTIFICATION_CHAT_ID
```
**Preparado para**: Sistema de notificaciones futuro

#### Variables de Rate Limiting:
```python
self.rate_limit_messages = int(os.getenv('RATE_LIMIT_MESSAGES', '10'))  # → RATE_LIMIT_MESSAGES
self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', '60'))      # → RATE_LIMIT_WINDOW
```
**Preparado para**: Control de velocidad de mensajes futuro

#### Variables de Desarrollo:
```python
self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'   # → DEBUG_MODE
self.dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'       # → DEV_MODE
```
**Preparado para**: Modos de desarrollo y debug

---

### 🎯 **Archivos que usan la configuración:**

#### `main.py`:
```python
from src.config import BotConfig

# En __init__:
self.config = BotConfig()  # ← Carga TODAS las variables de entorno

# Uso de credenciales:
self.client = TelegramClient('pequeno_bot_session', self.config.api_id, self.config.api_hash)
await self.client.start(bot_token=self.config.bot_token)
```

#### `src/handlers/event_handler.py`:
```python
def __init__(self, client, config):
    self.config = config  # ← Recibe la configuración completa
    # Tiene acceso a TODAS las variables de entorno via self.config.*
```

#### `src/handlers/command_handler.py`:
```python
def __init__(self, client, config):
    self.config = config  # ← Recibe la configuración completa
    
# Usado en comando /status:
📊 **Configuración:** {self.config.get_group_info()}
```

#### `src/database/manager.py`:
```python
def __init__(self, db_path: str = "data/bot_data.db"):
    # Usa el path por defecto, pero la configuración viene de DATABASE_URL
```

#### `src/utils/logger.py` (ACTUALIZADO):
```python
def setup_logger(name: str = "pequenoBot", level: str = None):
    # Usar variable de entorno si no se especifica nivel
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()  # ← LOG_LEVEL
    
    # Crear directorio de logs
    logs_dir = os.getenv('LOGS_DIR', 'logs')            # ← LOGS_DIR
    
    # Handler para archivo
    log_file_path = os.getenv('LOG_FILE', 'logs/bot.log') # ← LOG_FILE
```

---

## 🔄 **Flujo de Carga de Variables:**

1. **Inicio del Bot** (`main.py`)
   ```python
   self.config = BotConfig()  # ← Se ejecuta __init__ de BotConfig
   ```

2. **Carga de Variables** (`src/config/bot_config.py`)
   ```python
   load_dotenv()  # ← Carga el archivo .env
   # Todas las variables os.getenv() ahora tienen valores del .env
   ```

3. **Distribución** 
   - `self.config` se pasa a todos los handlers
   - Los handlers tienen acceso a toda la configuración
   - El logger usa directamente `os.getenv()` (actualizado)

---

## ✅ **Variables Actualmente Utilizadas:**

### 🟢 **En Uso Activo:**
- ✅ `API_ID`, `API_HASH`, `BOT_TOKEN` - Credenciales básicas
- ✅ `DATABASE_URL` - Base de datos SQLite
- ✅ `LOG_LEVEL`, `LOG_FILE`, `LOGS_DIR` - Sistema de logging
- ✅ `TARGET_GROUP_ID`, `TARGET_GROUP_USERNAME` - Configuración de grupo (opcional)

### 🟡 **Preparadas para Uso Futuro:**
- 🔶 `MAX_FILE_SIZE_MB`, `VIDEO_QUALITY`, `IMAGE_QUALITY` - Procesamiento de archivos
- 🔶 `ENABLE_NOTIFICATIONS`, `NOTIFICATION_CHAT_ID` - Sistema de notificaciones
- 🔶 `RATE_LIMIT_MESSAGES`, `RATE_LIMIT_WINDOW` - Control de velocidad
- 🔶 `DEBUG_MODE`, `DEV_MODE` - Modos de desarrollo
- 🔶 `TEMP_DIR`, `DATA_DIR`, `DOWNLOADS_DIR` - Directorios de trabajo

El sistema está diseñado para ser extensible - todas las variables están cargadas y disponibles para cuando se implementen las funcionalidades correspondientes.