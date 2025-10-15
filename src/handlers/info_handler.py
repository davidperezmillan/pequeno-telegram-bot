"""
Manejador de comandos de información para el bot pequeño
"""

import os
from datetime import datetime
from telethon import events
from telethon.tl.types import User, Chat, Channel
from src.config import setup_logger
from src.telegram_client import TelegramMessenger


class InfoHandler:
    """Clase para manejar comandos de información del bot"""
    
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.logger = setup_logger('InfoHandler')
        self.messenger = TelegramMessenger(client, config)
    
    def register_commands(self):
        """Registrar todos los comandos de información"""
        
        @self.client.on(events.NewMessage(pattern=r'/id'))
        async def cmd_id(event):
            """Comando /id - Muestra información completa de IDs"""
            try:
                await self._handle_id_command(event)
            except Exception as e:
                self.logger.error(f"Error en comando /id: {e}")
                await self.messenger.send_notification_to_me(
                    "❌ Error obteniendo información de IDs"
                )
        
        @self.client.on(events.NewMessage(pattern=r'/info'))
        async def cmd_info(event):
            """Comando /info - Información del bot"""
            try:
                await self._handle_info_command(event)
            except Exception as e:
                self.logger.error(f"Error en comando /info: {e}")
                await self.messenger.send_notification_to_me(
                    "❌ Error obteniendo información del bot"
                )
    
    async def _handle_id_command(self, event):
        """Manejar comando /id"""
        message = event.message
        chat = await event.get_chat()
        sender = await event.get_sender()
        
        # Información básica
        chat_info = self._get_chat_info(chat)
        sender_info = self._get_chat_info(sender) if sender else None
        
        # Construir respuesta
        response = "🆔 **INFORMACIÓN DE IDs**\n"
        response += "=" * 30 + "\n\n"
        
        # ID del mensaje
        response += f"📨 **Mensaje ID**: `{message.id}`\n"
        response += f"📅 **Fecha**: `{message.date}`\n\n"
        
        # Información del chat
        response += "🏠 **INFORMACIÓN DEL CHAT**\n"
        response += self._format_chat_info(chat_info) + "\n\n"
        
        # Información del remitente
        if sender_info:
            response += "👤 **INFORMACIÓN DEL REMITENTE**\n"
            response += self._format_chat_info(sender_info) + "\n\n"
        
        # Si es un reenvío, mostrar información original
        if message.forward:
            response += "📤 **MENSAJE REENVIADO**\n"
            if message.forward.chat:
                forward_chat_info = self._get_chat_info(message.forward.chat)
                response += self._format_chat_info(forward_chat_info) + "\n"
            if message.forward.sender:
                forward_sender_info = self._get_chat_info(message.forward.sender)
                response += "**Remitente original:**\n"
                response += self._format_chat_info(forward_sender_info) + "\n"
            response += "\n"
        
        # Si es una respuesta, mostrar información del mensaje original
        if message.reply_to_msg_id:
            response += "↩️ **RESPUESTA A MENSAJE**\n"
            response += f"📨 **Mensaje original ID**: `{message.reply_to_msg_id}`\n"
            
            try:
                original_msg = await event.get_reply_message()
                if original_msg and original_msg.sender:
                    original_sender_info = self._get_chat_info(original_msg.sender)
                    response += "**Autor original:**\n"
                    response += self._format_chat_info(original_sender_info) + "\n"
            except Exception as e:
                self.logger.warning(f"No se pudo obtener mensaje original: {e}")
            response += "\n"
        
        # Formato para copiar fácilmente
        response += "📋 **PARA COPIAR EN .ENV**\n"
        response += "```\n"
        if self._is_group_or_channel(chat_info):
            response += f"CHAT_TARGET={chat_info['id']}\n"
            if chat_info['username']:
                response += f"CHAT_TARGET_USERNAME={chat_info['username']}\n"
            else:
                response += f"# CHAT_TARGET_USERNAME= (no disponible)\n"
        else:
            response += f"# Este es un chat privado, no un grupo/canal\n"
            response += f"CHAT_ME={chat_info['id']}\n"
            if chat_info['username']:
                response += f"USERNAME={chat_info['username']}\n"
            else:
                response += f"# USERNAME= (no disponible)\n"
        response += "```"
        
        await self.messenger.send_notification_to_me(response, parse_mode='md')
        
        # Log del uso del comando
        username = sender_info['username'] if sender_info else 'sin_username'
        user_id = sender_info['id'] if sender_info else 'N/A'
        self.logger.info(f"Comando /id usado por {username} (ID: {user_id}) en chat {chat_info['id']}")
    
    async def _handle_info_command(self, event):
        """Manejar comando /info - Estado del bot y configuración"""
        chat = await event.get_chat()
        chat_info = self._get_chat_info(chat)
        
        response = "📊 **ESTADO DEL PEQUENO BOT**\n"
        response += "=" * 30 + "\n\n"
        
        # Información del chat actual
        response += "📍 **CHAT ACTUAL**\n"
        response += f"🏷️ **Nombre**: {chat_info['title']}\n"
        response += f"🆔 **ID**: `{chat_info['id']}`\n"
        response += f"📝 **Tipo**: {chat_info['type']}\n\n"
        
        # Configuración del bot
        response += "🎯 **CONFIGURACIÓN**\n"
        response += f"🆔 **Chat Target**: `{self.config.chat_target or 'No configurado'}`\n"
        response += f"👤 **Chat Me**: `{self.config.chat_me or 'No configurado'}`\n\n"
        
        # Verificar si estamos en el chat objetivo
        current_chat_id = chat_info['id']
        if self.config.chat_target:
            if current_chat_id == self.config.chat_target:
                response += "✅ **ESTADO**: Este ES el chat objetivo configurado\n"
                response += "🟢 **El bot procesa mensajes aquí**\n\n"
            else:
                response += "ℹ️ **ESTADO**: Este NO es el chat objetivo\n"
                response += f"📤 **Chat objetivo**: `{self.config.chat_target}`\n"
                response += f"📥 **Chat actual**: `{current_chat_id}`\n\n"
        else:
            response += "⚠️ **ESTADO**: No hay chat objetivo configurado\n"
            response += "🟡 **El bot procesa mensajes de todos los chats**\n\n"
        
        # Información del bot
        response += "🤖 **INFORMACIÓN DEL BOT**\n"
        me = await self.client.get_me()
        response += f"👤 **Nombre**: {me.first_name}\n"
        response += f"🆔 **ID**: `{me.id}`\n"
        response += f"📛 **Username**: @{me.username}\n\n"
        
        # Funcionalidades
        response += "🔧 **FUNCIONALIDADES DISPONIBLES**\n"
        response += "• 📝 Procesamiento de mensajes\n"
        response += "• 💾 Base de datos SQLite\n"
        response += "• 📨 Cliente de mensajería centralizado\n"
        response += "• 📊 Sistema de estadísticas\n"
        response += "• 🔄 Respuestas automáticas\n"
        response += "• 🎯 Notificaciones personales\n\n"
        
        response += "⏰ **TIEMPO**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        await self.messenger.send_notification_to_me(response, parse_mode='md')
        
        # Log del comando
        sender = await event.get_sender()
        username = getattr(sender, 'username', 'sin_username') if sender else 'desconocido'
        self.logger.info(f"Comando /info usado por {username} (ID: {sender.id if sender else 'N/A'}) en chat {current_chat_id}")
    
    def _get_chat_info(self, entity):
        """Obtener información de un chat/usuario"""
        if not entity:
            return None
        
        info = {
            'id': entity.id,
            'type': type(entity).__name__,
            'title': '',
            'username': getattr(entity, 'username', None),
            'first_name': getattr(entity, 'first_name', None),
            'last_name': getattr(entity, 'last_name', None),
        }
        
        # Determinar título según el tipo
        if isinstance(entity, User):
            if info['first_name']:
                info['title'] = info['first_name']
                if info['last_name']:
                    info['title'] += f" {info['last_name']}"
            elif info['username']:
                info['title'] = f"@{info['username']}"
            else:
                info['title'] = f"Usuario {entity.id}"
        elif isinstance(entity, (Chat, Channel)):
            info['title'] = getattr(entity, 'title', f"Chat {entity.id}")
        else:
            info['title'] = f"Entidad {entity.id}"
        
        return info
    
    def _format_chat_info(self, chat_info):
        """Formatear información del chat"""
        if not chat_info:
            return "No disponible"
        
        lines = []
        lines.append(f"🏷️ **Nombre**: {chat_info['title']}")
        lines.append(f"🆔 **ID**: `{chat_info['id']}`")
        lines.append(f"📝 **Tipo**: {chat_info['type']}")
        
        if chat_info['username']:
            lines.append(f"📛 **Username**: @{chat_info['username']}")
        
        if chat_info['first_name']:
            lines.append(f"👤 **Nombre**: {chat_info['first_name']}")
        
        if chat_info['last_name']:
            lines.append(f"👥 **Apellido**: {chat_info['last_name']}")
        
        return "\n".join(lines)
    
    def _is_group_or_channel(self, chat_info):
        """Verificar si es un grupo o canal"""
        return chat_info['type'] in ['Chat', 'Channel']