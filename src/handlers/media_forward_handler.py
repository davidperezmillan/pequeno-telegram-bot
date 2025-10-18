import os
from telethon import events
from telethon.tl.custom import Button
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage
from src.config import setup_logger
from src.telegram_client import TelegramMessenger
from src.utils.file_manager import FileManager
from src.database.manager import DatabaseManager
from src.database.models import Message
from src.utils.image_description_service import ImageDescriptionService


class MediaForwardHandler:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.logger = setup_logger('MediaForwardHandler')
        self.messenger = TelegramMessenger(client, config)
        self.file_manager = FileManager()
        self.db_manager = DatabaseManager()
        self.image_description_service = ImageDescriptionService()
      

    def register_handlers(self):

        @self.client.on(events.NewMessage(incoming=True))
        async def handle_incoming_message(event):
            """Handle incoming messages and forward them if necessary."""
            try:
                message_type = self._determine_message_type(event.message)
                if message_type in [ 'video', 'animation']:
                    await self._process_video(event.message)

                elif message_type in ['image']:
                    if getattr(self.config, 'image_processing_enabled', True):
                        await self._process_image(event.message)
                    else:
                        await self.messenger.send_notification_to_me("Procesamiento de imágenes desactivado por configuración.", parse_mode='md')
                
                elif message_type == 'text':
                    await self.messenger.send_notification_to_me("recuperamos un texto", parse_mode='md')

                elif message_type == 'sticker':
                    await self._process_sticker(event.message)

                else:
                    await self.messenger.send_notification_to_me("recuperamos otro tipo de mensaje", parse_mode='md')
            except Exception as e:
                self.logger.error(f"Error handling message: {e}")

    async def _process_video(self, message):
        """Process video messages."""
        file_info = self._get_file_info(message)
        long_video, reason = await self._should_download_file(file_info)

        if long_video:
            # Call the VideoProcessor for long videos
            await self._process_long_video(message, file_info, reason)
        else:
            await self._process_short_video(message)

        # Delete the video from the original chat
        await self.messenger.delete_message(message.id,message.chat_id)

    async def _process_image(self, message):
        """Process image messages."""
        file_info = self._get_file_info(message)
        
        # Send image with initial caption to the user's chat
        sent_message = await self._replay_with_buttons(message, caption="🖼️ Procesando imagen...")

        # Download the image
        file_name = file_info.get('file_name') if file_info else None
        downloaded_path = await self.messenger.download_media_from_message(message, file_name=file_name)
        
        if not downloaded_path:
            self.logger.error("Error al descargar la imagen")
            return
        
        self.logger.info(f"Imagen descargada: {downloaded_path}")

        # Generate descriptions using the description service
        ## descriptions = await self.image_description_service.describe_image_joy_local(downloaded_path)
        descriptions = await self.image_description_service.describe_image_blip_local(downloaded_path)
        
        # Edit message with English description
        try:
            await self.client.edit_message(
                sent_message.chat_id,
                sent_message.id,
                text=f"🖼️ **Descripción (EN):** {descriptions['english']}\n🔄 Traduciendo al español...",
                buttons=sent_message.buttons
            )
            self.logger.info("Mensaje actualizado con descripción en inglés")
        except Exception as e:
            self.logger.error(f"Error editando mensaje con descripción EN: {e}")

        # Edit message with final Spanish description
        try:
            await self.client.edit_message(
                sent_message.chat_id,
                sent_message.id,
                text=f"🖼️ **Descripción (EN):** {descriptions['english']}\n🖼️ **Descripción:** {descriptions['spanish']}\n🤖 **Modelo:** {descriptions['model_used']}",
                buttons=sent_message.buttons
            )
            self.logger.info("Mensaje actualizado con descripción en español")
        except Exception as e:
            self.logger.error(f"Error editando mensaje final: {e}")
            # Fallback: send description as separate message
            await self.messenger.send_notification_to_me(
                f"📝 **Descripción de la imagen:**\n{descriptions['spanish']}",
                parse_mode='md'
            )

        # Process the image (resize if large) using the description service
        processed_path = await self.image_description_service.process_image_file(
            downloaded_path, 
            max_size=(1920, 1080),
            quality=85
        )

        # Save the file path to the sent message in database
        message_obj = Message(
            message_id=sent_message.id,
            chat_id=sent_message.chat_id,
            user_id=self.config.chat_me,
            message_type='photo',
            media_info={'file_path': processed_path},
            created_at=sent_message.date
        )
        self.db_manager.save_message(message_obj)

        # Clean up original downloaded file if different from processed
        if processed_path != downloaded_path:
            await self.file_manager.cleanup_files([downloaded_path])

        # Delete the image from the original chat
        await self.messenger.delete_message(message.id, message.chat_id)

    async def _process_sticker(self, message):
        """Process sticker messages."""
        try:
            # Get file info
            file_info = self._get_file_info(message)
            
            # Download the sticker
            file_name = file_info.get('file_name') if file_info else None
            downloaded_path = await self.messenger.download_media_from_message(message, file_name=file_name)
            
            if not downloaded_path:
                self.logger.error("Error al descargar el sticker")
                await self.messenger.send_notification_to_me("❌ Error al descargar sticker", parse_mode='md')
                return
            
            self.logger.info(f"Sticker descargado: {downloaded_path}")
            
            # Send sticker with buttons to the user's chat
            sent_message = await self._replay_sticker_with_buttons(message, downloaded_path)
            
            # Save the file path to the sent message in database
            message_obj = Message(
                message_id=sent_message.id,
                chat_id=sent_message.chat_id,
                user_id=self.config.chat_me,
                message_type='sticker',
                media_info={'file_path': downloaded_path},
                created_at=sent_message.date
            )
            self.db_manager.save_message(message_obj)
            
            # Delete the sticker from the original chat
            await self.messenger.delete_message(message.id, message.chat_id)
            
        except Exception as e:
            self.logger.error(f"Error processing sticker: {e}")
            await self.messenger.send_notification_to_me(f"❌ Error procesando sticker: {str(e)}", parse_mode='md')

    async def _process_long_video(self, message, file_info, reason):

        
        # Send video with buttons to the user's chat
        sent_message = await self._replay_long_video_with_buttons(message, caption=f"**⚠️ Video largo detectado ⚠️ **\n🎬 tiempo: {file_info['file_size'] / (1024 * 1024):.2f} MB")

        # Descargar el video con mensajes de progreso
        downloaded_path = await self._download_with_progress(message, file_info, reason)
        
        if not downloaded_path:
            self.logger.error("Error al descargar el video largo")
            return
        
        self.logger.info(f"Video descargado exitosamente: {downloaded_path}")

        # Save the file path to the sent message in database
        message_obj = Message(
            message_id=sent_message.id,
            chat_id=sent_message.chat_id,
            user_id=self.config.chat_me,
            message_type='document',
            media_info={'file_path': downloaded_path},
            created_at=sent_message.date
        )
        self.db_manager.save_message(message_obj)

        # Crear 3 clips de 10 segundos aleatorios
        lClip_path, clips_creados = await self.create_clips(downloaded_path, num_clips=3, clip_duration=10)


        # Limpiar archivos temporales
        await self.file_manager.cleanup_files(lClip_path)

            


    async def _process_short_video(self, message):
        # Send video with buttons to the user's chat
        await self._replay_with_buttons(message)

    def _determine_message_type(self, message):
        """Determine the type of the message."""
        if message.text and not message.media:
            return 'text'

        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                return 'image'
            elif isinstance(message.media, MessageMediaDocument):
                document = message.media.document
                if document.mime_type:
                    if document.mime_type.startswith('video/'):
                        return 'video'
                    elif 'gif' in document.mime_type:
                        return 'animation'
                    elif document.mime_type.startswith('image/'):
                        return 'image'
                    elif any(hasattr(attr, 'stickerset') for attr in document.attributes):
                        return 'sticker'
            elif isinstance(message.media, MessageMediaWebPage):
                return 'text'  # Message with a link preview

        return 'unknown'
    
    def _get_file_info(self, message):
        """Obtener información del archivo en el mensaje"""
        if not message.media:
            return None
        
        file_info = {
            'has_file': False,
            'file_type': None,
            'file_size': 0,
            'file_name': None,
            'mime_type': None
        }
        
        if isinstance(message.media, MessageMediaDocument):
            document = message.media.document
            file_info['has_file'] = True
            file_info['file_size'] = document.size
            file_info['mime_type'] = document.mime_type
            
            # Obtener nombre del archivo
            for attr in document.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    file_info['file_name'] = attr.file_name
                    break
            
            # Determinar tipo de archivo
            if document.mime_type:
                if document.mime_type.startswith('video/'):
                    file_info['file_type'] = 'video'
                elif document.mime_type.startswith('image/'):
                    file_info['file_type'] = 'animation' if 'gif' in document.mime_type else 'image'
                elif 'sticker' in document.mime_type or any(hasattr(attr, 'stickerset') for attr in document.attributes):
                    file_info['file_type'] = 'sticker'
        
        elif isinstance(message.media, MessageMediaPhoto):
            file_info['has_file'] = True
            file_info['file_type'] = 'image'
            file_info['mime_type'] = 'image/jpeg'
            # Las fotos no tienen tamaño directo, estimamos
            file_info['file_size'] = 0  # Se calculará si es necesario
        
        return file_info
    

    async def _should_download_file(self, file_info):
        """Determinar si el archivo debe ser descargado"""
        max_file_size_bytes = self.config.max_file_size_mb * 1024 * 1024


        if not file_info or not file_info['has_file']:
            return False, "No hay archivo"
        
        # Verificar tamaño para videos
        if file_info['file_type'] == 'video':
            if file_info['file_size'] > max_file_size_bytes:
                return True, f"Video grande detectado: {file_info['file_size'] / (1024*1024):.1f}MB"
            else:
                return False, f"Video pequeño: {file_info['file_size'] / (1024*1024):.1f}MB"
        
        # Por ahora, otros tipos no se descargan automáticamente
        return False, f"Tipo {file_info['file_type']} - pendiente de definir"


    async def _download_with_progress(self, message, file_info, reason):
        """
        Descarga un archivo con mensajes de progreso en tiempo real.
        
        Args:
            message: Mensaje de Telegram con el archivo
            file_info: Información del archivo
            reason: Razón de la descarga
            
        Returns:
            str: Ruta del archivo descargado o None si falló
        """
        # Enviar mensaje inicial de descarga
        progress_message = await self.messenger.send_notification_to_me(
            f"📥 Iniciando descarga...\n📊 Tamaño: {file_info['file_size'] / (1024*1024):.1f}MB\n📝 {reason}\n🔗 Origen: Mensaje {message.id} en chat {message.chat_id}", 
            parse_mode='md'
        )
        
        # Crear callback de progreso
        async def progress_callback(current, total):
            if total > 0:
                percentage = (current / total) * 100
                self.logger.debug(f"Progreso de descarga: {percentage:.1f}% ({current}/{total} bytes)")
                if self._send_notif_process(percentage):
                    self.logger.info(f"Progreso de descarga: {percentage:.1f}% ({current}/{total} bytes)")
                    try:
                        await self.messenger.edit_message(
                            progress_message.id,
                            f"📥 Descargando...\n📊 Progreso: {percentage:.1f}%\n📏 {current/(1024*1024):.1f}MB / {total/(1024*1024):.1f}MB\n📝 {reason}\n🔗 Origen: Mensaje {message.id} en chat {message.chat_id}",
                            chat_id=self.config.chat_me,
                            parse_mode='md'
                        )
                        
                    except Exception as e:
                        # Silenciar errores de edición de mensaje (pueden ocurrir por límites de tiempo o permisos)
                        self.logger.debug(f"No se pudo actualizar progreso: {e}")
                        pass
        
        # Descargar el archivo con callback de progreso
        self.logger.info(f"Descargando archivo: {reason}")
        self.logger.info(f"info del archivo: {file_info}")
        file_name = file_info.get('file_name') if file_info else None
        downloaded_path = await self.messenger.download_media_from_message(
            message, 
            progress_callback=progress_callback,
            file_name=file_name
        )
        
        if not downloaded_path:
            # Actualizar mensaje de error
            try:
                await self.messenger.edit_message(
                    progress_message.id,
                    f"❌ Error al descargar archivo\n📊 Tamaño: {file_info['file_size'] / (1024*1024):.1f}MB\n📝 {reason}\n🔗 Origen: Mensaje {message.id} en chat {message.chat_id}",
                    chat_id=self.config.chat_me,
                    parse_mode='md'
                )
            except Exception as e:
                self.logger.warning(f"No se pudo actualizar mensaje de error: {e}")
            self.logger.error(f"Error al descargar archivo: {reason}")
            return None
        
        # Actualizar mensaje de éxito
        try:
            await self.messenger.edit_message(
                progress_message.id,
                f"✅ Archivo descargado exitosamente\n📁 Archivo: {downloaded_path}\n📊 Tamaño: {file_info['file_size'] / (1024*1024):.1f}MB\n📝 {reason}",
                chat_id=self.config.chat_me,
                parse_mode='md'
            )
        except Exception as e:
            self.logger.warning(f"No se pudo actualizar mensaje de éxito: {e}")
        
        self.logger.info(f"Archivo descargado exitosamente: {downloaded_path}")
        # borrar los mensajes de descarga
        try:
            await self.messenger.delete_message(progress_message.id, progress_message.chat_id)
        except Exception as e:
            self.logger.warning(f"No se pudo borrar mensaje de progreso: {e}")
            pass

        return downloaded_path
    
    async def _replay_with_buttons(self, message, caption=None):
        # Send video with buttons to the user's chat
        buttons = [
            [
                Button.inline("Enviar al chat destino", b"send_to_target"),
                Button.inline("Descartar", b"discard")
            ],
            [
                Button.inline("Descargar y crear clips", b"download_and_create_clips"),
                Button.inline("Borrar archivo", b"delete_file")
            ]
        ]

        sent_message = await self.client.send_file(
            self.config.chat_me, 
            file=message.media, 
            caption=caption,
            buttons=buttons
        )
        
        return sent_message
    
    async def _replay_long_video_with_buttons(self, message, caption=None):
        # Send long video with additional button for creating new clips
        buttons = [
            [
                Button.inline("Enviar al chat destino", b"send_to_target"),
                Button.inline("Descartar", b"discard")
            ],
            [
                Button.inline("Crear nuevos clips", b"create_new_clips"),
                Button.inline("Borrar archivo", b"delete_file")
            ]
        ]

        sent_message = await self.client.send_file(
            self.config.chat_me, 
            file=message.media, 
            caption=caption,
            buttons=buttons
        )
        
        return sent_message
    
    async def _replay_sticker_with_buttons(self, message, file_path):
        """Send sticker with buttons to the user's chat."""
        buttons = [
            [
                Button.inline("Enviar al chat destino", b"send_to_target"),
                Button.inline("Descartar", b"discard")
            ],
            [
                Button.inline("Borrar archivo", b"delete_file")
            ]
        ]

        sent_message = await self.client.send_file(
            self.config.chat_me, 
            file=file_path,
            caption="🎭 Sticker recibido",
            buttons=buttons
        )
        
        return sent_message
    
    async def create_clips(self, downloaded_path,num_clips=3, clip_duration=10):
        lClip_path = []
        clips_creados = 0
        


        for i in range(num_clips):
            self.logger.info(f"Creando clip {i+1}/{num_clips} de {clip_duration} segundos...")
            # Crear nombre único para el clip
            base_name = os.path.splitext(downloaded_path)[0]  # Nombre sin extensión
            extension = os.path.splitext(downloaded_path)[1]   # Extensión con punto
            clip_path = f"{base_name}_clip_{i:02d}{extension}"
            success, result = await self.file_manager.create_random_video_clip(
                input_path=downloaded_path,
                output_path=clip_path,
                clip_duration=clip_duration
            )
            
            if success:
                lClip_path.append(result)
                clips_creados += 1
                self.logger.info(f"Clip {i+1}/3 creado exitosamente: {result}")

                # Enviar mensaje de progreso
                progress_message = await self.client.send_message(
                    self.config.chat_me, 
                    f"Creando clip {i+1}/{num_clips}..."
                )

                # Enviar el clip como respuesta al mensaje de progreso
                try:
                    buttons = [
                        [
                            Button.inline("Enviar al chat destino", b"send_to_target"),
                            Button.inline("Descartar", b"discard")
                        ]
                    ]

                    sent_message = await self.client.send_file(
                        self.config.chat_me,
                        file=result,
                        reply_to=progress_message.id,
                        parse_mode='markdown',
                        buttons=buttons
                    )
                    
                    # Editar el mensaje de progreso para confirmar
                    await self.client.edit_message(
                        progress_message.chat_id,
                        progress_message.id,
                        text=f"✅ Clip {i+1}/{num_clips} creado y enviado."
                    )
                    
                    # Save message with file path to database
                    message_obj = Message(
                        message_id=sent_message.id,
                        chat_id=sent_message.chat_id,
                        user_id=self.config.chat_me,
                        message_type='document',
                        media_info={'file_path': result},
                        created_at=sent_message.date
                    )
                    self.db_manager.save_message(message_obj)
                    
                    self.logger.info(f"Clip {i+1}/3 enviado exitosamente a chat_me")
                except Exception as e:
                    self.logger.error(f"Error enviando clip {i+1}/3 a chat_me: {e}")
                    # Editar mensaje de progreso en caso de error
                    try:
                        await self.client.edit_message(
                            progress_message.chat_id,
                            progress_message.id,
                            text=f"❌ Error enviando clip {i+1}/{num_clips}."
                        )
                    except:
                        pass    

            else:
                self.logger.error(f"Error creando clip {i+1}/3: {result}")
        return lClip_path, clips_creados
    

    def _send_notif_process(self, percentage):
        # solo enviar actualización si el proceso esta entre:
        # - 25-30% (primer cuarto)
        # - 50-60% (mitad)
        # - 75-80% (último cuarto)
        # - 90-100% (final)
        if (percentage >= 20 and percentage < 21) or \
           (percentage >= 40 and percentage < 41) or \
           (percentage >= 50 and percentage < 51) or \
           (percentage >= 60 and percentage < 61) or \
           (percentage >= 80 and percentage < 81) or \
           (percentage >= 99 and percentage < 100):
            return True
        return False