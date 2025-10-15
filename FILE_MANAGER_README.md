# FileManager - Gestión de Archivos Multimedia

La clase `FileManager` proporciona funcionalidades para gestionar archivos multimedia, especialmente videos, con capacidad para crear clips aleatorios.

## Funcionalidades

- **Obtención de duración de video**: Usa `ffprobe` para obtener la duración exacta de videos
- **Cálculo de inicio aleatorio**: Calcula un punto de inicio aleatorio asegurando que el clip completo quepa
- **Creación de clips**: Crea clips de video usando `ffmpeg` con parámetros optimizados
- **Limpieza de archivos**: Elimina archivos temporales de forma segura
- **Información de archivos**: Obtiene metadatos básicos de archivos

## Métodos Principales

### `create_random_video_clip(input_path, output_path, clip_duration=30)`

Crea un clip de video cortado desde un punto aleatorio del video original.

**Parámetros:**
- `input_path` (str): Ruta del video original
- `output_path` (str): Ruta donde guardar el clip
- `clip_duration` (int): Duración del clip en segundos (default: 30)

**Retorna:**
- `Tuple[bool, str]`: (éxito, mensaje/ruta del clip o error)

**Ejemplo:**
```python
file_manager = FileManager()

# Crear un clip de 30 segundos aleatorio
exito, resultado = await file_manager.create_random_video_clip(
    input_path="/videos/video_largo.mp4",
    output_path="/videos/clip_aleatorio.mp4",
    clip_duration=30
)

if exito:
    print(f"Clip creado: {resultado}")
else:
    print(f"Error: {resultado}")
```

### `get_video_duration(video_path)`

Obtiene la duración del video en segundos.

**Parámetros:**
- `video_path` (str): Ruta al archivo de video

**Retorna:**
- `float` o `None`: Duración en segundos, o None si hay error

### `calculate_random_start_time(video_duration, clip_duration)`

Calcula un tiempo de inicio aleatorio para el clip.

**Parámetros:**
- `video_duration` (float): Duración total del video
- `clip_duration` (int): Duración deseada del clip

**Retorna:**
- `int`: Tiempo de inicio en segundos

### `cleanup_files(file_paths)`

Elimina archivos temporales.

**Parámetros:**
- `file_paths` (list): Lista de rutas de archivos a eliminar

**Retorna:**
- `Tuple[int, list]`: (archivos eliminados, archivos con error)

## Requisitos

- `ffmpeg` y `ffprobe` instalados en el sistema
- Python 3.7+
- Dependencias: `ffmpeg-python` (aunque la implementación actual usa subprocess)

## Uso en el Bot

```python
from src.utils.file_manager import FileManager

# En un handler o procesador
file_manager = FileManager()

# Procesar un video recibido
async def procesar_video(video_path):
    clip_path = video_path.replace('.mp4', '_clip.mp4')

    exito, resultado = await file_manager.create_random_video_clip(
        input_path=video_path,
        output_path=clip_path,
        clip_duration=30
    )

    if exito:
        # Enviar el clip por Telegram
        await enviar_clip_telegram(clip_path)

        # Limpiar archivos temporales
        await file_manager.cleanup_files([video_path, clip_path])
```

## Características del Corte Aleatorio

- **Inicio inteligente**: El punto de inicio se calcula para asegurar que el clip completo quepa en el video
- **Margen de seguridad**: Mínimo 5 segundos desde el inicio, margen suficiente al final
- **Copia de streams**: Usa `-c copy` cuando es posible para procesamiento rápido
- **Re-encoding**: Si es necesario, usa `libx264` y `aac` para compatibilidad
- **Logging detallado**: Registra todas las operaciones para debugging