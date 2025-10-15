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

#### Variables Opcionales (Chats Específicos):
```python
# Configuración de chats específicos
self.chat_me = self._get_optional_env('CHAT_ME', int)                      # → CHAT_ME
self.chat_target = self._get_optional_env('CHAT_TARGET', int)              # → CHAT_TARGET
```
**Usado en**: `src/telegram_client.py` → TelegramMessenger para envío de mensajes y notificaciones

#### Variables de Procesamiento:
```python
self.max_file_size_mb = self._get_optional_env('MAX_FILE_SIZE_MB', int, 20) # → MAX_FILE_SIZE_MB
```
**Usado en**: Validación de tamaño de archivos multimedia

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
- ✅ `CHAT_ME`, `CHAT_TARGET` - Chats específicos para mensajería
- ✅ `DATABASE_URL` - Base de datos SQLite
- ✅ `DOWNLOADS_DIR` - Directorio para descargas
- ✅ `LOG_LEVEL`, `LOG_FILE` - Sistema de logging
- ✅ `MAX_FILE_SIZE_MB` - Límite de tamaño de archivos

### 🟡 **Con Valores por Defecto:**
- 🔶 `DATA_DIR` (default: 'data') - Directorio de datos
- 🔶 `LOGS_DIR` (default: 'logs') - Directorio de logs  
- 🔶 `TEMP_DIR` (default: 'temp') - Directorio temporal

### 🟡 **Preparadas para Uso Futuro:**
- 🔶 `TARGET_GROUP_ID`, `TARGET_GROUP_USERNAME` - Configuración de grupo (opcional)
- 🔶 `VIDEO_QUALITY`, `IMAGE_QUALITY` - Procesamiento de archivos
- 🔶 `ENABLE_NOTIFICATIONS`, `NOTIFICATION_CHAT_ID` - Sistema de notificaciones
- 🔶 `RATE_LIMIT_MESSAGES`, `RATE_LIMIT_WINDOW` - Control de velocidad
- 🔶 `DEBUG_MODE`, `DEV_MODE` - Modos de desarrollo

El sistema está diseñado para ser extensible - todas las variables están cargadas y disponibles para cuando se implementen las funcionalidades correspondientes.