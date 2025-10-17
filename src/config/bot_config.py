"""
Configuración del bot pequeno
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class BotConfig:
    """Clase de configuración para el bot pequeno"""
    
    def __init__(self):
        """Inicializar configuración desde variables de entorno"""
        
        # Credenciales de Telegram API
        self.api_id = self._get_required_env('API_ID', int)
        self.api_hash = self._get_required_env('API_HASH')
        self.bot_token = self._get_required_env('BOT_TOKEN')
        
        # Configuración del grupo objetivo (opcional)
        self.target_group_id = self._get_optional_env('TARGET_GROUP_ID', int)
        self.target_group_username = self._get_optional_env('TARGET_GROUP_USERNAME')
        
        # Configuración de chats específicos
        self.chat_me = self._get_optional_env('CHAT_ME', int)
        self.chat_target = self._get_optional_env('CHAT_TARGET', int)
        self.max_file_size_mb = self._get_optional_env('MAX_FILE_SIZE_MB', int, 20)
        
        # Configuración de base de datos
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///data/bot_data.db')
        
        # Configuración de directorios
        self.temp_dir = os.getenv('TEMP_DIR', 'temp')
        self.data_dir = os.getenv('DATA_DIR', 'data')
        self.logs_dir = os.getenv('LOGS_DIR', 'logs')
        self.downloads_dir = os.getenv('DOWNLOADS_DIR', 'downloads')
        # Activar/desactivar tratamiento de imágenes
        self.image_processing_enabled = os.getenv('IMAGE_PROCESSING_ENABLED', 'true').lower() == 'true'
        # Configuración de logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/bot.log')
  
        
        # Validar configuración crítica
        self._validate_config()
    
    def _get_required_env(self, key: str, type_converter=str):
        """Obtener variable de entorno requerida"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Variable de entorno requerida no encontrada: {key}")
        
        try:
            return type_converter(value) if type_converter != str else value
        except (ValueError, TypeError) as e:
            raise ValueError(f"Error al convertir variable {key}: {e}")
    
    def _get_optional_env(self, key: str, type_converter=str, default=None):
        """Obtener variable de entorno opcional"""
        value = os.getenv(key, '').strip()
        if not value:
            return default
        
        try:
            return type_converter(value) if type_converter != str else value
        except (ValueError, TypeError):
            return default
    
    def _validate_config(self):
        """Validar que la configuración sea coherente"""
        
        # Validar credenciales
        if not isinstance(self.api_id, int) or self.api_id <= 0:
            raise ValueError("API_ID debe ser un número entero positivo")
        
        if not self.api_hash or len(self.api_hash) < 32:
            raise ValueError("API_HASH parece ser inválido")
        
        if not self.bot_token or ':' not in self.bot_token:
            raise ValueError("BOT_TOKEN parece ser inválido")
    
    @property
    def is_group_restricted(self) -> bool:
        """Indica si el bot está restringido a un grupo específico"""
        return self.target_group_id is not None or self.target_group_username is not None
    
    def get_group_info(self) -> str:
        """Obtener información del grupo objetivo"""
        if not self.is_group_restricted:
            return "🌍 Bot configurado para funcionar en TODOS los grupos"
        
        info_parts = []
        if self.target_group_id:
            info_parts.append(f"ID={self.target_group_id}")
        if self.target_group_username:
            info_parts.append(f"Username=@{self.target_group_username}")
        
        return f"🎯 Bot configurado para grupo específico: {', '.join(info_parts)}"
    def __str__(self):
        """Representación string de la configuración (sin mostrar tokens)"""
        return (f"BotConfig(API_ID={self.api_id}, "
                f"debug_mode={self.debug_mode})")
    
    def __repr__(self):
        return self.__str__()