from telethon import events
from src.config import setup_logger
from src.database.manager import DatabaseManager
from src.database.models import Message
import os

class CallbackHandler:
    def __init__(self, client, config, media_forward_handler=None):
        self.client = client
        self.config = config
        self.logger = setup_logger('CallbackHandler')
        self.db_manager = DatabaseManager()
        self.media_forward_handler = media_forward_handler

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
                    # Answer the callback first
                    await event.answer("Procesando eliminación...")
                    
                    self.logger.info("User chose to delete the file from filesystem.")
                    # Get the message from database to find file path
                    message_obj = self.db_manager.get_message(original_message.id, original_message.chat_id)
                    if message_obj and message_obj.media_info and 'file_path' in message_obj.media_info:
                        file_path = message_obj.media_info['file_path']
                        self.logger.debug(f"Attempting to delete file at path: {file_path}")
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            self.logger.info(f"Archivo {file_path} eliminado del sistema de archivos")
                            await event.answer("Archivo eliminado correctamente.")
                        else:
                            await event.answer("Archivo no encontrado.")
                    else:
                        await event.answer("Información del archivo no disponible.")
                    
                    # Delete the message from chat
                    await original_message.delete()
                elif data == "create_new_clips":
                    # Answer the callback first
                    await event.answer("Creando nuevos clips...")
                    
                    self.logger.info("User chose to create new clips from the video.")
                    
                    # Get the message from database to find file path
                    message_obj = self.db_manager.get_message(original_message.id, original_message.chat_id)
                    if message_obj and message_obj.media_info and 'file_path' in message_obj.media_info:
                        file_path = message_obj.media_info['file_path']
                        self.logger.debug(f"Creating new clips from file: {file_path}")
                        
                        if os.path.exists(file_path) and self.media_forward_handler:
                            try:
                                # Create new clips
                                lClip_path, clips_creados = await self.media_forward_handler.create_clips(
                                    file_path, num_clips=3, clip_duration=10
                                )
                                
                                # Clean up temporary files
                                await self.media_forward_handler.file_manager.cleanup_files(lClip_path)
                                
                                await event.answer(f"✅ {clips_creados} nuevos clips creados y enviados.")
                                self.logger.info(f"Created {clips_creados} new clips from {file_path}")
                            except Exception as e:
                                self.logger.error(f"Error creating new clips: {e}")
                                await event.answer("❌ Error al crear los clips.")
                        else:
                            await event.answer("❌ Archivo no encontrado o servicio no disponible.")
                    else:
                        await event.answer("❌ Información del archivo no disponible.")
                elif data == "download_and_create_clips":
                    # Answer the callback first
                    await event.answer("Descargando y creando clips...")
                    
                    self.logger.info("User chose to download and create clips from short video.")
                    
                    if self.media_forward_handler:
                        try:
                            # Get file info
                            file_info = self.media_forward_handler._get_file_info(original_message)
                            
                            # Download the video
                            downloaded_path = await self.media_forward_handler._download_with_progress(
                                original_message, file_info, "Procesando video corto como largo"
                            )
                            
                            if not downloaded_path:
                                await event.answer("❌ Error al descargar el video.")
                                return
                            
                            # Save to database
                            message_obj = Message(
                                message_id=original_message.id,
                                chat_id=original_message.chat_id,
                                user_id=self.config.chat_me,
                                message_type='document',
                                media_info={'file_path': downloaded_path},
                                created_at=original_message.date
                            )
                            self.db_manager.save_message(message_obj)
                            
                            # Create clips
                            lClip_path, clips_creados = await self.media_forward_handler.create_clips(
                                downloaded_path, num_clips=3, clip_duration=10
                            )
                            
                            # Clean up temporary files
                            await self.media_forward_handler.file_manager.cleanup_files(lClip_path)
                            
                            await event.answer(f"✅ {clips_creados} clips creados y enviados.")
                            self.logger.info(f"Downloaded and created {clips_creados} clips from short video")
                            
                            # Delete the original message
                            await original_message.delete()
                        except Exception as e:
                            self.logger.error(f"Error downloading and creating clips: {e}")
                            await event.answer("❌ Error al procesar el video.")
                    else:
                        await event.answer("❌ Servicio no disponible.")
                else:
                    await event.answer("Acción desconocida.")
            except Exception as e:
                self.logger.error(f"Error handling callback: {e}")