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
        # Inicializar los pipelines (se cargan cuando se usan)
        self.caption_pipeline = None
        self.translation_pipeline = None

    async def describe_image(self, image_path: str) -> str:
        """
        Describe una imagen usando un modelo de Hugging Face y traduce a español

        Args:
            image_path: Ruta de la imagen

        Returns:
            str: Descripción de la imagen en español
        """
        try:
            self.logger.info(f"Describiendo imagen: {image_path}")

            # Inicializar el pipeline de descripción si no está cargado
            if self.caption_pipeline is None:
                self.logger.info("Cargando modelo de descripción de imágenes...")
                self.caption_pipeline = pipeline(
                    "image-to-text",
                    model="nlpconnect/vit-gpt2-image-captioning",
                    device="cpu"
                )

            # Abrir imagen
            image = Image.open(image_path)

            # Generar descripción en inglés
            result = self.caption_pipeline(image)
            english_description = result[0]['generated_text'] if result else "No se pudo generar descripción"

            self.logger.info(f"Descripción en inglés: {english_description}")

            # Traducir a español
            spanish_description = await self._translate_to_spanish(english_description)

            self.logger.info(f"Descripción en español: {spanish_description}")
            return spanish_description

        except Exception as e:
            self.logger.error(f"Error describiendo imagen {image_path}: {e}")
            return f"Error al describir la imagen: {str(e)}"

    async def _translate_to_spanish(self, text: str) -> str:
        """
        Traduce texto del inglés al español

        Args:
            text: Texto en inglés

        Returns:
            str: Texto en español
        """
        try:
            # Inicializar el pipeline de traducción si no está cargado
            if self.translation_pipeline is None:
                self.logger.info("Cargando modelo de traducción inglés-español...")
                self.translation_pipeline = pipeline(
                    "translation",
                    model="Helsinki-NLP/opus-mt-en-es",
                    device="cpu"
                )

            # Traducir
            result = self.translation_pipeline(text)
            translated = result[0]['translation_text'] if result else text

            return translated

        except Exception as e:
            self.logger.error(f"Error traduciendo texto: {e}")
            return text  # Devolver original si falla la traducción

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