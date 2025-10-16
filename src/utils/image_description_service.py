import asyncio
from PIL import Image
from transformers import pipeline
from src.config import setup_logger
from src.utils.image_processor import ImageProcessor


class ImageDescriptionService:
    """Service for generating AI-powered image descriptions and translations."""

    def __init__(self):
        self.logger = setup_logger('ImageDescriptionService')
        self.image_processor = ImageProcessor()
        self.caption_pipeline = None

    async def describe_image(self, image_path: str) -> dict:
        """
        Generate English description and Spanish translation for an image.

        Args:
            image_path: Path to the image file

        Returns:
            dict: Contains 'english' and 'spanish' descriptions
        """
        try:
            self.logger.info(f"Generando descripción completa para: {image_path}")

            # Generate English description
            english_description = await self._get_english_description(image_path)

            # Translate to Spanish
            spanish_description = await self.image_processor._translate_to_spanish(english_description)

            return {
                'english': english_description,
                'spanish': spanish_description
            }

        except Exception as e:
            self.logger.error(f"Error generando descripción completa: {e}")
            return {
                'english': 'Error generating description',
                'spanish': 'Error generando descripción'
            }

    async def _get_english_description(self, image_path: str) -> str:
        """Get English description without translation."""
        try:
            self.logger.info(f"Generando descripción en inglés: {image_path}")

            # Initialize caption pipeline if needed
            if self.caption_pipeline is None:
                self.logger.info("Cargando modelo de descripción de imágenes...")
                self.caption_pipeline = pipeline(
                    "image-to-text",
                    model="nlpconnect/vit-gpt2-image-captioning",
                    device="cpu"
                )

            # Open image
            image = Image.open(image_path)

            # Generate description
            result = self.caption_pipeline(image)
            description = result[0]['generated_text'] if result else "No se pudo generar descripción"

            self.logger.info(f"Descripción en inglés generada: {description}")
            return description

        except Exception as e:
            self.logger.error(f"Error generando descripción en inglés {image_path}: {e}")
            return "Error al generar descripción"

    async def process_image_file(self, image_path: str, max_size=(1920, 1080), quality=85) -> str:
        """
        Process image file (resize if necessary).

        Args:
            image_path: Path to the image file
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (0-100)

        Returns:
            str: Path to processed image
        """
        try:
            processed_path = await self.image_processor.process_image(
                image_path,
                max_size=max_size,
                quality=quality
            )
            return processed_path
        except Exception as e:
            self.logger.error(f"Error procesando imagen {image_path}: {e}")
            return image_path  # Return original path if processing fails