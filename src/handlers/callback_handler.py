from telethon import events
from src.config import setup_logger
from src.database.manager import DatabaseManager
import os

class CallbackHandler:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.logger = setup_logger('CallbackHandler')
        self.db_manager = DatabaseManager()

    def register_handlers(self):
        @self.client.on(events.CallbackQuery())
        async def handle_callback(event):
            """Handle button callbacks."""
            try:
                self.logger.info(f"Callback data received: {event.data}")

                # Ensure we fetch the original message
                original_message = await event.get_message()
                data = event.data.decode("utf-8")


                if data == "send_to_target":
                    self.logger.info("User chose to send video to target chat.")
                    # Forward the video to the target chat
                    await self.client.send_file(
                        self.config.chat_target,
                        original_message.media,
                        parse_mode='markdown',
                        supports_streaming=True,
                        spoiler=True
                      )
                    # Borrar el video del chat del usuario
                    await original_message.delete()  # Delete after sending
                elif data == "discard":
                    # Delete the video from the user's chat
                    await original_message.delete()  # Use the fetched message
                    await event.answer("Video descartado y eliminado.")
                elif data == "delete_file":
                    self.logger.info("User chose to delete the file from filesystem.")
                    # Get the message from database to find file path
                    message_obj = self.db_manager.get_message(original_message.id, original_message.chat_id)
                    if message_obj and message_obj.media_info and 'file_path' in message_obj.media_info:
                        file_path = message_obj.media_info['file_path']
                        self.logger.debug(f"Attempting to delete file at path: {file_path}")
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            self.logger.info(f"Archivo {file_path} eliminado del sistema de archivos")
                            await event.answer("Archivo eliminado del sistema de archivos.")
                        else:
                            await event.answer("Archivo no encontrado en el sistema de archivos.")
                    else:
                        await event.answer("Información del archivo no disponible.")
                    # Delete the message from chat
                    await original_message.delete()
                else:
                    await event.answer("Acción desconocida.")
            except Exception as e:
                self.logger.error(f"Error handling callback: {e}")