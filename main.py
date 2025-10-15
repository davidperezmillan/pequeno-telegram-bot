import os
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, FloodWaitError

from src.config import BotConfig, setup_logger
from src.handlers import CommandHandler, InfoHandler 
from src.handlers import CallbackHandler
from src.handlers import MediaForwardHandler
from src.telegram_client import TelegramMessenger



class pequenoBot:
    def __init__(self):
        # Inicializar configuración
        self.config = BotConfig()
        
        # Crear cliente de Telethon usando la configuración
        self.client = TelegramClient('pequeno_bot_session', self.config.api_id, self.config.api_hash)
        
        # Inicializar handlers
        self.info_handler = InfoHandler(self.client, self.config)
        self.media_forward_handler = MediaForwardHandler(self.client, self.config)

        # inicializar commend
        self.command_handler = CommandHandler(self.client, self.config)

        # inicializar callback
        self.callback_handler = CallbackHandler(self.client, self.config)
        
        # Inicializar cliente de mensajería
        self.messenger = TelegramMessenger(self.client, self.config)
        
        # Configurar logger
        self.logger = setup_logger('pequeno_bot')
        
    async def start(self):
        """Iniciar el bot"""
        try:
            # Conectar cliente con manejo de FloodWaitError
            try:
                await self.client.start(bot_token=self.config.bot_token)
                self.logger.info("Bot iniciado correctamente")
            except FloodWaitError as e:
                self.logger.warning(f"FloodWaitError: Esperando {e.seconds} segundos antes de reconectar...")
                await asyncio.sleep(e.seconds)
                await self.client.start(bot_token=self.config.bot_token)
                self.logger.info("Bot iniciado correctamente después de esperar")
            
            # Obtener información del bot
            me = await self.client.get_me()
            self.logger.info(f"Bot conectado como: @{me.username}")
            self.logger.info(f"ID del bot: {me.id}")

            # Configuración de grupos objetivo
            self.logger.info(self.config.get_group_info())
            
            # Registrar handlers de eventos
            self.media_forward_handler.register_handlers()
            self.command_handler.register_commands()
            self.info_handler.register_commands()
            self.callback_handler.register_handlers()  # Ensure callback handler is registered
            self.logger.info("✅ Todos los handlers registrados correctamente")

            # Mantener el bot corriendo
            self.logger.info("🚀 pequeno Bot en funcionamiento...")
            await self.client.run_until_disconnected()
            
        except Exception as e:
            self.logger.error(f"Error al iniciar pequeno Bot: {e}")
            raise
    
async def main():
    bot = pequenoBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())