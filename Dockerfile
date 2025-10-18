FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    sqlite3 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-cargar modelos de Hugging Face para acelerar el inicio
RUN python -c "from transformers import DetrImageProcessor, DetrForObjectDetection, ViTImageProcessor, ViTForImageClassification; print('Downloading DETR...'); DetrImageProcessor.from_pretrained('facebook/detr-resnet-50'); DetrForObjectDetection.from_pretrained('facebook/detr-resnet-50'); print('Downloading AdamCodd NSFW...'); ViTImageProcessor.from_pretrained('AdamCodd/vit-base-nsfw-detector'); ViTForImageClassification.from_pretrained('AdamCodd/vit-base-nsfw-detector'); print('Models preloaded.')"

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs /app/downloads /app/detections

# Ejecutar el bot
CMD ["python", "main.py"]