"""
Sistema de logging para el bot
"""

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = "pequenoBot", level: str = None) -> logging.Logger:
    """
    Configurar el sistema de logging
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               Si es None, se usa la variable de entorno LOG_LEVEL
    
    Returns:
        Logger configurado
    """
    
    # Usar variable de entorno si no se especifica nivel
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Crear directorio de logs si no existe
    logs_dir = os.getenv('LOGS_DIR', 'logs')
    log_dir = Path(logs_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Configurar el logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicar handlers si ya están configurados
    if logger.handlers:
        return logger
    
    # Formato del log con información adicional
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d - %(funcName)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo - usar variable de entorno LOG_FILE
    log_file_path = 'logs/bot.log'
    log_file = Path(log_file_path)
    
    # Crear directorio del archivo de log si no existe
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = "pequenoBot") -> logging.Logger:
    """
    Obtener una instancia del logger
    
    Args:
        name: Nombre del logger
    
    Returns:
        Logger existente o nuevo
    """
    return logging.getLogger(name)