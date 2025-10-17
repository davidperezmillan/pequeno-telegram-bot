import asyncio
import os
import torch
from PIL import Image
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
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

    async def describe_image_blip_local(self, image_path: str) -> dict:
        """
        Generate image description using local BLIP model.

        Args:
            image_path: Path to the image file

        Returns:
            dict: Contains 'english', 'spanish', and 'model_used' descriptions
        """
        try:
            self.logger.info(f"Generando descripción con blip local: {image_path}")

            # Try BLIP only
            try:
                english_description = await self._describe_with_blip(image_path)
                model_used = "BLIP"
            except Exception as e:
                self.logger.warning(f"Blip falló: {e}")
                return {
                    'english': 'Error generating description',
                    'spanish': '',
                    'model_used': 'BLIP'
                } 

            # Translate to Spanish
            spanish_description = await self.image_processor._translate_to_spanish(english_description)

            return {
                'english': english_description,
                'spanish': spanish_description,
                'model_used': model_used
            }

        except Exception as e:
            self.logger.error(f"Error generando descripción con JoyCaption local {image_path}: {e}")
            return {
                'english': 'Error generating description',
                'spanish': 'Error generando descripción',
                'model_used': 'Error'
            }


    async def _describe_with_blip(self, image_path: str) -> str:
        """Describe image using BLIP model as fallback."""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            # Load BLIP model
            processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
            model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

            image = Image.open(image_path).convert('RGB')
         
            text = "a photography of"
            # Generate description
            inputs = processor(image, text, return_tensors="pt")
            # Genera la caption con parámetros para mayor longitud y diversidad
            outputs = model.generate(
                **inputs,
                max_new_tokens=1000,  # aumenta máximo tokens para texto más largo
                num_beams=5,          # usa beam search para mejor calidad
                temperature=0.9,      # controla diversidad y creatividad
                early_stopping=True
            )
            description = processor.decode(outputs[0], skip_special_tokens=True)

            self.logger.info(f"Descripción BLIP generada: {description}")
            
            return description.strip()

        except Exception as e:
            self.logger.error(f"Error con BLIP: {e}")
            raise


   

