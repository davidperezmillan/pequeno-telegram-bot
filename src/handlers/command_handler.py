"""
Manejador de comandos para el bot de Telegram
"""

from telethon import events
from src.config import setup_logger
from src.database import DatabaseManager
from src.telegram_client import TelegramMessenger


class CommandHandler:
    def __init__(self, client, config):
        """
        Inicializar el manejador de comandos
        
        Args:
            client: Cliente de Telethon
            config: Configuración del bot
        """
        self.client = client
        self.config = config
        self.logger = setup_logger('command_handler')
        self.db_manager = DatabaseManager()
        self.messenger = TelegramMessenger(client, config)
    
    def register_commands(self):
        """Registrar todos los comandos del bot"""
        
        @self.client.on(events.NewMessage(pattern=r'/start'))
        async def start_command(event):
            """Comando /start"""
            try:
                await self.messenger.reply_to_message(
                    "🤖 ¡Hola! Soy el pequeno Bot. Estoy procesando mensajes correctamente.",
                    event.message.id
                )
                self.logger.info(f"Comando /start ejecutado por usuario {event.sender_id}")
            except Exception as e:
                self.logger.error(f"Error en comando /start: {e}")
        
        @self.client.on(events.NewMessage(pattern=r'/ping'))
        async def ping_command(event):
            """Comando /ping"""
            try:
                await self.messenger.reply_to_message(
                    "🏓 Pong! El bot está funcionando correctamente.",
                    event.message.id
                )
                self.logger.info(f"Comando /ping ejecutado por usuario {event.sender_id}")
            except Exception as e:
                self.logger.error(f"Error en comando /ping: {e}")
        
        @self.client.on(events.NewMessage(pattern=r'/help'))
        async def help_command(event):
            """Comando /help"""
            try:
                help_text = """
🤖 **pequeno Bot - Comandos disponibles:**

📝 **Comandos básicos:**
• /start - Iniciar el bot
• /ping - Verificar que el bot esté funcionando
• /help - Mostrar esta ayuda
• /status - Ver el estado del bot
• /stats - Ver estadísticas de mensajes guardados

🆔 **Comandos de información:**
• /id - Obtener información completa de IDs (mensaje, chat, usuario)
• /info - Estado detallado del bot y configuración

🧪 **Comandos de prueba del messenger:**
• /test_messenger - Probar configuración del cliente
• /send_test - Enviar mensaje de prueba al chat target
• /send_notification - Enviar notificación personal

🔧 **El bot procesa automáticamente:**
• Todos los mensajes de texto
• Mensajes con archivos multimedia
• Mensajes editados
• Guarda todo en la base de datos
                """
                await self.messenger.reply_to_message(help_text, event.message.id)
                self.logger.info(f"Comando /help ejecutado por usuario {event.sender_id}")
            except Exception as e:
                self.logger.error(f"Error en comando /help: {e}")
        
        @self.client.on(events.NewMessage(pattern=r'/status'))
        async def status_command(event):
            """Comando /status"""
            try:
                # Información básica del bot
                me = await self.client.get_me()
                status_text = f"""
🤖 **Estado del pequeno Bot:**

✅ **Estado:** Funcionando correctamente
👤 **Usuario:** @{me.username}
🆔 **ID:** {me.id}
📊 **Configuración:** {self.config.get_group_info()}
                """
                await self.messenger.reply_to_message(status_text, event.message.id)
                self.logger.info(f"Comando /status ejecutado por usuario {event.sender_id}")
            except Exception as e:
                self.logger.error(f"Error en comando /status: {e}")
        
        @self.client.on(events.NewMessage(pattern=r'/stats'))
        async def stats_command(event):
            """Comando /stats - Mostrar estadísticas de la base de datos"""
            try:
                stats = self.db_manager.get_message_stats()
                
                if not stats:
                    await self.messenger.reply_to_message(
                        "❌ Error obteniendo estadísticas de la base de datos",
                        event.message.id
                    )
                    return
                
                # Formatear estadísticas
                stats_text = f"""
📊 **Estadísticas de mensajes:**

📈 **General:**
• Total de mensajes: {stats.get('total_messages', 0)}

📝 **Por tipo de mensaje:**
"""
                
                # Agregar estadísticas por tipo
                for msg_type, count in stats.get('by_type', {}).items():
                    stats_text += f"• {msg_type}: {count}\n"
                
                # Top chats
                top_chats = stats.get('top_chats', [])
                if top_chats:
                    stats_text += "\n🏆 **Top chats (más activos):**\n"
                    for chat in top_chats[:5]:  # Solo top 5
                        title = chat.get('title', f"Chat {chat.get('chat_id')}")
                        count = chat.get('count', 0)
                        stats_text += f"• {title}: {count} mensajes\n"
                
                # Actividad últimos 7 días
                last_days = stats.get('last_7_days', [])
                if last_days:
                    stats_text += "\n📅 **Últimos 7 días:**\n"
                    for day in last_days:
                        date = day.get('date', 'N/A')
                        count = day.get('count', 0)
                        stats_text += f"• {date}: {count} mensajes\n"
                
                await self.messenger.reply_to_message(stats_text, event.message.id)
                self.logger.info(f"Comando /stats ejecutado por usuario {event.sender_id}")
                
            except Exception as e:
                self.logger.error(f"Error en comando /stats: {e}")
                await self.messenger.reply_to_message(
                    "❌ Error obteniendo estadísticas",
                    event.message.id
                )
        
        @self.client.on(events.NewMessage(pattern=r'/test_messenger'))
        async def test_messenger_command(event):
            """Comando /test_messenger - Probar el cliente de mensajería"""
            try:
                chat_info = self.messenger.get_chat_info()
                
                test_text = f"""
🧪 **Test del Cliente de Mensajería**

📊 **Configuración de Chats:**
• Chat Me: {chat_info['chat_me'] or 'No configurado'}
• Chat Target: {chat_info['chat_target'] or 'No configurado'}
• Estado: {'✅ Listo' if chat_info['has_chat_me'] and chat_info['has_chat_target'] else '⚠️ Configuración incompleta'}

💡 **Comandos disponibles:**
• /send_test - Enviar mensaje de prueba
• /send_notification - Enviar notificación personal
                """
                
                await self.messenger.reply_to_message(test_text, event.message.id)
                self.logger.info(f"Comando /test_messenger ejecutado por usuario {event.sender_id}")
                
            except Exception as e:
                self.logger.error(f"Error en comando /test_messenger: {e}")
                await self.messenger.reply_to_message(
                    "❌ Error probando cliente de mensajería",
                    event.message.id
                )
        
        @self.client.on(events.NewMessage(pattern=r'/send_test'))
        async def send_test_command(event):
            """Comando /send_test - Enviar mensaje de prueba al chat target"""
            try:
                if not self.config.chat_target:
                    await self.messenger.reply_to_message(
                        "❌ CHAT_TARGET no configurado",
                        event.message.id
                    )
                    return
                
                test_message = f"""
🎯 **Mensaje de Prueba**

Enviado desde pequeno Bot
Hora: {event.date}
Usuario: {event.sender_id}
                """
                
                result = await self.messenger.send_text_message(test_message)
                
                if result:
                    await self.messenger.reply_to_message(
                        "✅ Mensaje de prueba enviado correctamente",
                        event.message.id
                    )
                else:
                    await self.messenger.reply_to_message(
                        "❌ Error enviando mensaje de prueba",
                        event.message.id
                    )
                
                self.logger.info(f"Comando /send_test ejecutado por usuario {event.sender_id}")
                
            except Exception as e:
                self.logger.error(f"Error en comando /send_test: {e}")
                await self.messenger.reply_to_message(
                    "❌ Error en comando de prueba",
                    event.message.id
                )
        
        @self.client.on(events.NewMessage(pattern=r'/send_notification'))
        async def send_notification_command(event):
            """Comando /send_notification - Enviar notificación personal"""
            try:
                if not self.config.chat_me:
                    await self.messenger.reply_to_message(
                        "❌ CHAT_ME no configurado",
                        event.message.id
                    )
                    return
                
                notification = f"""
🔔 **Notificación del Bot**

El usuario {event.sender_id} ejecutó el comando /send_notification
Hora: {event.date}
                """
                
                result = await self.messenger.send_notification_to_me(notification)
                
                if result:
                    await self.messenger.reply_to_message(
                        "✅ Notificación enviada",
                        event.message.id
                    )
                else:
                    await self.messenger.reply_to_message(
                        "❌ Error enviando notificación",
                        event.message.id
                    )
                
                self.logger.info(f"Comando /send_notification ejecutado por usuario {event.sender_id}")
                
            except Exception as e:
                self.logger.error(f"Error en comando /send_notification: {e}")
                await self.messenger.reply_to_message(
                    "❌ Error enviando notificación",
                    event.message.id
                )