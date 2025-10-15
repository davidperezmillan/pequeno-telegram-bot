"""
Procesador de imágenes para el bot de Telegram
"""

import os
import asyncio
from PIL import Image
from transformers import pipeline
from src.config import setup_logger


class ImageProcessor:
    """Clase para procesar imágenes: redimensionar, convertir formatos, describir con IA"""

    def __init__(self):
        self.logger = setup_logger('ImageProcessor')
        # Inicializar el pipeline de descripción de imágenes (se carga cuando se usa)
        self.caption_pipeline = None

    async def describe_image(self, image_path: str) -> str:
        """
        Describe una imagen usando un modelo de Hugging Face sin censura

        Args:
            image_path: Ruta de la imagen

        Returns:
            str: Descripción de la imagen
        """
        try:
            self.logger.info(f"Describiendo imagen: {image_path}")

            # Inicializar el pipeline si no está cargado
            if self.caption_pipeline is None:
                self.logger.info("Cargando modelo de descripción de imágenes...")
                # Usar un modelo de captioning sin restricciones
                self.caption_pipeline = pipeline(
                    "image-to-text",
                    model="nlpconnect/vit-gpt2-image-captioning",
                    device="cpu"  # Cambiar a "cuda" si hay GPU
                )

            # Abrir imagen
            image = Image.open(image_path)

            # Generar descripción
            result = self.caption_pipeline(image)
            description = result[0]['generated_text'] if result else "No se pudo generar descripción"

            self.logger.info(f"Descripción generada: {description}")
            return description

        except Exception as e:
            self.logger.error(f"Error describiendo imagen {image_path}: {e}")
            return f"Error al describir la imagen: {str(e)}"

    async def process_image(self, input_path: str, output_path: str = None,
                          max_size: tuple = (1920, 1080), quality: int = 85,
                          format: str = None) -> str:
        """
        Procesa una imagen: redimensiona si es necesario y optimiza

        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida (opcional)
            max_size: Tamaño máximo (ancho, alto)
            quality: Calidad de compresión (1-100)
            format: Formato de salida ('JPEG', 'PNG', etc.)

        Returns:
            str: Ruta del archivo procesado
        """
        try:
            self.logger.info(f"Procesando imagen: {input_path}")

            # Abrir imagen
            with Image.open(input_path) as img:
                # Convertir a RGB si es necesario
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # Redimensionar si es más grande que max_size
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    self.logger.info(f"Imagen redimensionada a {img.size}")

                # Determinar formato de salida
                if not format:
                    format = 'JPEG' if input_path.lower().endswith(('.jpg', '.jpeg')) else 'PNG'

                # Generar ruta de salida si no se proporciona
                if not output_path:
                    input_dir = os.path.dirname(input_path)
                    base_name = os.path.splitext(os.path.basename(input_path))[0]
                    extension = 'jpg' if format == 'JPEG' else format.lower()
                    output_path = os.path.join(input_dir, f"{base_name}_processed.{extension}")

                # Crear directorio si no existe
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Guardar imagen procesada
                if format == 'JPEG':
                    img.save(output_path, format, quality=quality, optimize=True)
                else:
                    img.save(output_path, format)

                self.logger.info(f"Imagen procesada guardada en: {output_path}")
                return output_path

        except Exception as e:
            self.logger.error(f"Error procesando imagen {input_path}: {e}")
            raise