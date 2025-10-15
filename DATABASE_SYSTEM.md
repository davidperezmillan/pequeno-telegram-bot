# Sistema de Gestión de Base de Datos para pequeno Bot

## Resumen de Implementación

Hemos implementado un sistema completo de gestión de base de datos SQLite para el bot de Telegram que captura y almacena todos los mensajes que pasan por el bot.

## Estructura del Sistema

### 📁 Archivos Creados

```
src/database/
├── __init__.py         # Exporta las clases principales
├── models.py           # Modelos de datos (User, Chat, Message)
└── manager.py          # Gestor principal de la base de datos (DatabaseManager)
```

### 🗄️ Estructura de la Base de Datos

#### Tabla `users`
- `user_id` (INTEGER PRIMARY KEY) - ID único del usuario
- `username` (TEXT) - Nombre de usuario de Telegram
- `first_name` (TEXT) - Nombre del usuario
- `last_name` (TEXT) - Apellido del usuario
- `is_bot` (BOOLEAN) - Si es un bot o no
- `language_code` (TEXT) - Código de idioma
- `created_at` (TIMESTAMP) - Fecha de creación
- `updated_at` (TIMESTAMP) - Última actualización

#### Tabla `chats`
- `chat_id` (INTEGER PRIMARY KEY) - ID único del chat
- `title` (TEXT) - Título del chat/grupo
- `chat_type` (TEXT) - Tipo: 'private', 'group', 'supergroup', 'channel'
- `username` (TEXT) - Username del chat (si existe)
- `description` (TEXT) - Descripción del chat
- `member_count` (INTEGER) - Número de miembros
- `created_at` (TIMESTAMP) - Fecha de creación
- `updated_at` (TIMESTAMP) - Última actualización

#### Tabla `messages`
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - ID interno único
- `message_id` (INTEGER) - ID del mensaje en Telegram
- `chat_id` (INTEGER) - ID del chat (FK)
- `user_id` (INTEGER) - ID del usuario (FK)
- `text` (TEXT) - Texto del mensaje
- `message_type` (TEXT) - Tipo: 'text', 'photo', 'video', 'document', etc.
- `media_info` (TEXT) - JSON con información adicional de media
- `reply_to_message_id` (INTEGER) - ID del mensaje al que responde
- `forward_from_chat_id` (INTEGER) - Chat origen si es reenviado
- `forward_from_message_id` (INTEGER) - Mensaje origen si es reenviado
- `edit_date` (TIMESTAMP) - Fecha de edición (si aplica)
- `created_at` (TIMESTAMP) - Fecha de creación
- `raw_data` (TEXT) - JSON completo del mensaje original

## 🔧 Funcionalidades Implementadas

### 1. Modelos de Datos (`models.py`)
- **User**: Representación de usuarios de Telegram
- **Chat**: Representación de chats/grupos
- **Message**: Representación de mensajes con soporte para diferentes tipos
- Métodos de conversión a/desde diccionarios y desde eventos de Telethon

### 2. Gestor de Base de Datos (`manager.py`)
- **DatabaseManager**: Clase principal para gestión de la BD
- Context manager para conexiones seguras
- Métodos CRUD para usuarios, chats y mensajes
- Estadísticas avanzadas de mensajes
- Procesamiento automático de eventos de Telethon

### 3. Integración con Handlers
- **EventHandler**: Actualizado para guardar mensajes automáticamente
- **CommandHandler**: Nuevo comando `/stats` para ver estadísticas
- Logging mejorado con indicadores de estado de BD

## 📊 Comandos Disponibles

### Comandos Existentes Actualizados
- `/start` - Iniciar el bot
- `/ping` - Verificar funcionamiento
- `/help` - Ayuda (actualizada con nueva funcionalidad)
- `/status` - Estado del bot

### Comando Nuevo
- `/stats` - Mostrar estadísticas detalladas de la base de datos:
  - Total de mensajes guardados
  - Distribución por tipo de mensaje
  - Top 5 chats más activos
  - Actividad de los últimos 7 días

## 🚀 Características Técnicas

### Seguridad y Robustez
- Context managers para gestión segura de conexiones
- Manejo de errores en todas las operaciones
- Logging detallado de todas las operaciones
- Transacciones seguras con rollback automático

### Rendimiento
- Índices en campos clave para consultas rápidas
- Consultas optimizadas para estadísticas
- Uso de `INSERT OR REPLACE` para evitar duplicados

### Escalabilidad
- Estructura modular y extensible
- Fácil agregación de nuevos campos o tablas
- Soporte para diferentes tipos de media

## 🎯 Flujo de Funcionamiento

1. **Recepción de Mensaje**: El EventHandler detecta un nuevo mensaje
2. **Procesamiento Automático**: DatabaseManager.process_telethon_event()
3. **Extracción de Datos**: Se extraen datos del usuario, chat y mensaje
4. **Almacenamiento**: Se guardan/actualizan en las tablas correspondientes
5. **Logging**: Se registra el éxito/fallo de la operación
6. **Estadísticas**: Los datos están disponibles para consultas vía `/stats`

## ✅ Verificación de Funcionamiento

Se ha probado el sistema con éxito:
- ✅ Creación de tablas automática
- ✅ Inserción de usuarios de prueba
- ✅ Inserción de chats de prueba  
- ✅ Inserción de mensajes de prueba
- ✅ Generación de estadísticas
- ✅ Integración con handlers

## 📝 Notas de Uso

- La base de datos se crea automáticamente en `data/bot_data.db`
- Los mensajes se guardan con información completa incluyendo metadata
- El sistema es tolerante a fallos y continúa funcionando aunque haya errores de BD
- Las estadísticas se actualizan en tiempo real
- Soporte completo para mensajes de texto, imágenes, videos, documentos, etc.

El sistema está listo para ser usado en producción y capturará todos los mensajes que pasen por el bot automáticamente.