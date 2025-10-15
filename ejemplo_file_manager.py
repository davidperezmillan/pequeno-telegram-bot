#!/usr/bin/env python3
"""
Ejemplo de uso de la clase FileManager para cortar videos aleatoriamente
"""

import asyncio
from pathlib import Path
from src.utils.file_manager import FileManager

async def ejemplo_corte_video_aleatorio():
    """
    Ejemplo de cómo usar FileManager para crear un clip aleatorio de un video
    """
    file_manager = FileManager()

    # Ruta del video original (debe existir)
    video_original = "/ruta/a/tu/video.mp4"

    # Ruta donde guardar el clip
    clip_salida = "/ruta/a/tu/clip_aleatorio.mp4"

    # Duración del clip en segundos
    duracion_clip = 30

    print(f"Procesando video: {video_original}")

    # Crear clip aleatorio
    exito, resultado = await file_manager.create_random_video_clip(
        input_path=video_original,
        output_path=clip_salida,
        clip_duration=duracion_clip
    )

    if exito:
        print(f"✅ Clip creado exitosamente: {resultado}")

        # Obtener información del archivo creado
        info = file_manager.get_file_info(resultado)
        if info:
            print(f"📊 Tamaño del clip: {info['size_mb']:.2f} MB")

    else:
        print(f"❌ Error creando clip: {resultado}")

    # Limpiar archivos temporales (opcional)
    # await file_manager.cleanup_files([clip_salida])

if __name__ == "__main__":
    # Ejecutar el ejemplo
    asyncio.run(ejemplo_corte_video_aleatorio())