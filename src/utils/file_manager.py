import os
import asyncio
import json
import random
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from src.config.logger import get_logger

logger = get_logger()

class FileManager:
    """
    Gestor de archivos para operaciones de procesamiento multimedia

    Funcionalidades:
    1. Gestión de archivos de video
    2. Recorte de videos con inicio aleatorio
    3. Obtención de metadatos de video
    4. Limpieza de archivos temporales
    """

    def __init__(self):
        self.logger = logger

    async def get_video_duration(self, video_path: str) -> Optional[float]:
        """
        Obtener la duración del video en segundos usando ffprobe

        Args:
            video_path (str): Ruta al archivo de video

        Returns:
            float: Duración del video en segundos, o None si hay error
        """
        try:
            # Usar ffprobe para obtener la duración
            result = subprocess.run([
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'json',
                video_path
            ], capture_output=True, text=True)

            if result.returncode != 0:
                self.logger.error(f"Error ejecutando ffprobe: {result.stderr}")
                return None

            # Parsear la salida JSON
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])

            self.logger.info(f"Duración del video detectada: {duration:.2f}s")
            return duration

        except Exception as e:
            self.logger.error(f"Error obteniendo duración del video: {e}")
            return None

    def calculate_random_start_time(self, video_duration: float, clip_duration: int) -> int:
        """
        Calcular un tiempo de inicio aleatorio para el clip

        Args:
            video_duration (float): Duración total del video en segundos
            clip_duration (int): Duración deseada del clip en segundos

        Returns:
            int: Tiempo de inicio en segundos
        """
        if video_duration <= clip_duration:
            # Si el video es más corto que el clip deseado, empezar desde el inicio
            return 0

        # Calcular el rango válido para el inicio del clip
        # Dejar un margen al final para que el clip completo quepa
        max_start_time = int(video_duration - clip_duration)

        # Asegurar que tenemos al menos 5 segundos de margen al inicio
        min_start_time = min(5, max_start_time)

        if max_start_time <= min_start_time:
            return min_start_time

        # Generar tiempo aleatorio
        random_start = random.randint(min_start_time, max_start_time)

        self.logger.info(f"Tiempo de inicio aleatorio calculado: {random_start}s (rango: {min_start_time}-{max_start_time}s)")
        return random_start

    async def create_random_video_clip(
        self,
        input_path: str,
        output_path: str,
        clip_duration: int = 30
    ) -> Tuple[bool, str]:
        """
        Crear un clip de video cortado desde un punto aleatorio

        Args:
            input_path (str): Ruta del video original
            output_path (str): Ruta donde guardar el clip
            clip_duration (int): Duración del clip en segundos (default: 30)

        Returns:
            Tuple[bool, str]: (éxito, mensaje/ruta del clip o error)
        """
        try:
            self.logger.info(f"Creando clip aleatorio: {input_path} -> {output_path} (duración: {clip_duration}s)")

            # Obtener duración del video
            video_duration = await self.get_video_duration(input_path)
            if video_duration is None:
                return False, "No se pudo obtener la duración del video"

            # Calcular tiempo de inicio aleatorio
            start_offset = self.calculate_random_start_time(video_duration, clip_duration)

            # Crear el clip usando ffmpeg
            result = subprocess.run([
                'ffmpeg',
                '-i', input_path,
                '-ss', str(start_offset),
                '-t', str(clip_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-y',
                output_path
            ], capture_output=True, text=True)

            if result.returncode != 0:
                return False, f"Error en ffmpeg: {result.stderr}"

            # Verificar que el archivo se creó
            if not os.path.exists(output_path):
                return False, "El clip no se generó correctamente"

            clip_size = os.path.getsize(output_path)
            self.logger.info(f"Clip creado exitosamente: {output_path} ({clip_size} bytes)")

            return True, output_path

        except Exception as e:
            error_msg = f"Error creando clip de video: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    async def cleanup_files(self, file_paths: list) -> Tuple[int, list]:
        """
        Limpiar archivos temporales

        Args:
            file_paths (list): Lista de rutas de archivos a eliminar

        Returns:
            Tuple[int, list]: (archivos eliminados exitosamente, archivos con error)
        """
        deleted_files = []
        failed_deletions = []

        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    self.logger.info(f"Archivo eliminado: {file_path}")
                else:
                    self.logger.warning(f"Archivo no encontrado: {file_path}")
            except Exception as e:
                failed_deletions.append(f"{file_path}: {str(e)}")
                self.logger.error(f"Error eliminando {file_path}: {e}")

        return len(deleted_files), failed_deletions

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Obtener información básica de un archivo

        Args:
            file_path (str): Ruta del archivo

        Returns:
            dict: Información del archivo o None si hay error
        """
        try:
            if not os.path.exists(file_path):
                return None

            stat = os.stat(file_path)
            return {
                'path': file_path,
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'exists': True
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo información del archivo {file_path}: {e}")
            return None