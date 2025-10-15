# Cliente de Mensajería de Telegram - TelegramMessenger

## 📋 **Descripción**

La clase `TelegramMessenger` es una interfaz completa para interactuar con Telegram, permitiendo enviar y gestionar diferentes tipos de contenido multimedia y mensajes.

## 🔧 **Configuración Requerida**

### Variables de Entorno Nuevas:

```properties
# Chat personal del bot contigo (para notificaciones y control)
CHAT_ME=14824267

# Chat objetivo donde el bot enviará contenido
CHAT_TARGET=-1001234567890
```

### En `src/config/bot_config.py`:

```python
# Configuración de chats específicos
self.chat_me = self._get_optional_env('CHAT_ME', int)
self.chat_target = self._get_optional_env('CHAT_TARGET', int)
```

## 🚀 **Características**

### ✅ **Tipos de Mensajes Soportados:**

1. **📝 Mensajes de Texto**
   - Texto plano o con formato (Markdown/HTML)
   - Respuesta a mensajes específicos
   - Edición de mensajes existentes

2. **📸 Imágenes**
   - Envío de fotos con caption
   - Soporte para múltiples formatos

3. **🎥 Videos**
   - Videos con metadatos (duración, resolución)
   - Soporte para streaming
   - Caption personalizable

4. **🎬 Animaciones/GIFs**
   - Envío como animaciones de Telegram
   - Optimizado para GIFs

5. **🔖 Stickers**
   - Envío de stickers personalizados

6. **📄 Documentos**
   - Cualquier tipo de archivo
   - Forzar como documento o detección automática

7. **📚 Álbumes Multimedia**
   - Hasta 10 archivos por álbum
   - Combinación de fotos y videos
   - Caption en el primer elemento

### 🛡️ **Gestión de Errores:**

- **FloodWait**: Manejo automático de límites de velocidad
- **Archivos faltantes**: Verificación de existencia
- **Chats no configurados**: Validación de configuración
- **Reintento automático**: En casos de errores temporales

## 📖 **Uso Básico**

### Inicialización:

```python
from src.telegram_client import TelegramMessenger

# En tu bot
messenger = TelegramMessenger(self.client, self.config)
```

### Ejemplos de Uso:

#### Enviar Mensaje de Texto:
```python
await messenger.send_text_message(
    "Hola mundo!", 
    chat_id=-1001234567890,  # Opcional, usa CHAT_TARGET por defecto
    parse_mode='md'
)
```

#### Editar Mensaje:
```python
await messenger.edit_message(
    message_id=123,
    new_text="Texto editado",
    chat_id=-1001234567890
)
```

#### Enviar Imagen:
```python
await messenger.send_photo(
    photo_path="ruta/a/imagen.jpg",
    caption="**Mi imagen**",
    parse_mode='md'
)
```

#### Enviar Video:
```python
await messenger.send_video(
    video_path="ruta/a/video.mp4",
    caption="Mi video",
    duration=30,
    width=1920,
    height=1080,
    supports_streaming=True
)
```

#### Enviar Álbum:
```python
file_paths = [
    "foto1.jpg",
    "foto2.jpg", 
    "video1.mp4"
]
await messenger.send_album(
    file_paths=file_paths,
    caption="Mi álbum multimedia"
)
```

#### Notificación Personal:
```python
await messenger.send_notification_to_me(
    "⚠️ Algo importante pasó en el bot"
)
```

## 🎯 **Comandos de Prueba Integrados**

### `/test_messenger`
Muestra la configuración actual de chats y estado del cliente:

```
🧪 Test del Cliente de Mensajería

📊 Configuración de Chats:
• Chat Me: 14824267
• Chat Target: -1001234567890
• Estado: ✅ Listo

💡 Comandos disponibles:
• /send_test - Enviar mensaje de prueba
• /send_notification - Enviar notificación personal
```

### `/send_test`
Envía un mensaje de prueba al `CHAT_TARGET`:

```
🎯 Mensaje de Prueba

Enviado desde pequeno Bot
Hora: 2025-10-13 15:30:00
Usuario: 14824267
```

### `/send_notification`
Envía una notificación al `CHAT_ME`:

```
🔔 Notificación del Bot

El usuario 14824267 ejecutó el comando /send_notification
Hora: 2025-10-13 15:30:00
```

## 🔄 **Integración en el Bot Principal**

### En `main.py`:
```python
from src.telegram_client import TelegramMessenger

class pequenoBot:
    def __init__(self):
        # ... configuración existente ...
        
        # Inicializar cliente de mensajería
        self.messenger = TelegramMessenger(self.client, self.config)
```

### En handlers:
```python
class CommandHandler:
    def __init__(self, client, config):
        # ... inicialización existente ...
        
        # Importar para evitar dependencias circulares
        from ..telegram_client import TelegramMessenger
        self.messenger = TelegramMessenger(client, config)
```

## 📊 **Logging**

Todos los métodos incluyen logging detallado:

```
✅ Mensaje de texto enviado a -1001234567890
📸 Imagen enviada a -1001234567890: /ruta/imagen.jpg
🎥 Video enviado a -1001234567890: /ruta/video.mp4
📚 Álbum enviado a -1001234567890: 3 archivos
⏰ FloodWait: 30s
❌ Error enviando mensaje: [detalles del error]
```

## ⚙️ **Métodos Disponibles**

| Método | Descripción | Parámetros Principales |
|--------|-------------|----------------------|
| `send_text_message()` | Enviar texto | `text`, `chat_id`, `parse_mode` |
| `edit_message()` | Editar mensaje | `message_id`, `new_text`, `chat_id` |
| `send_photo()` | Enviar imagen | `photo_path`, `caption`, `chat_id` |
| `send_video()` | Enviar video | `video_path`, `caption`, `duration`, etc. |
| `send_animation()` | Enviar GIF/animación | `animation_path`, `caption` |
| `send_sticker()` | Enviar sticker | `sticker_path`, `chat_id` |
| `send_document()` | Enviar documento | `document_path`, `caption`, `force_document` |
| `send_album()` | Enviar álbum | `file_paths`, `caption` |
| `send_notification_to_me()` | Notificación personal | `message` |
| `delete_message()` | Eliminar mensaje | `message_id`, `chat_id` |
| `get_chat_info()` | Info de configuración | - |

## 🔐 **Validaciones y Seguridad**

- ✅ Verificación de archivos existentes antes del envío
- ✅ Validación de configuración de chats
- ✅ Manejo automático de FloodWait
- ✅ Logging de todas las operaciones
- ✅ Límite de 10 archivos por álbum (Telegram API)
- ✅ Reintento automático en errores temporales

## 🚦 **Estados de Retorno**

- **Éxito**: Retorna el objeto mensaje de Telethon
- **Error**: Retorna `None` y registra el error en logs
- **Edición exitosa**: Retorna `True`
- **Error de edición**: Retorna `False`

El cliente está completamente integrado y listo para usar en producción con manejo robusto de errores y logging detallado.