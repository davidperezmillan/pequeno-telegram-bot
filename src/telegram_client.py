"""
Cliente de Telegram para envío de mensajes y contenido multimedia
"""

import os
import asyncio
from typing import List, Optional, Union, Any, Dict
from pathlib import Path
from telethon import TelegramClient
from telethon.errors import FloodWaitError, MessageNotModifiedError
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
from src.config import setup_logger


class TelegramMessenger:
    """Clase para gestionar el envío de mensajes y contenido multimedia en Telegram"""
    
    def __init__(self, client: TelegramClient, config):
        """
        Inicializar el cliente de mensajería
        
        Args:
            client: Cliente de Telethon ya autenticado
            config: Configuración del bot con chat_me y chat_target
        """
        self.client = client
        self.config = config
        self.logger = setup_logger('telegram_messenger')
        
        # Verificar configuración de chats
        if not config.chat_me:
            self.logger.warning("CHAT_ME no configurado - algunas funciones pueden no funcionar")
        if not config.chat_target:
            self.logger.warning("CHAT_TARGET no configurado - algunas funciones pueden no funcionar")
    
    async def send_text_message(
        self, 
        text: str, 
        chat_id: Optional[int] = None,
        parse_mode: str = 'md',
        reply_to: Optional[int] = None
    ) -> Optional[Any]:
        """
        Enviar mensaje de texto
        
        Args:
            text: Texto del mensaje
            chat_id: ID del chat (usa chat_target por defecto)
            parse_mode: Modo de parseo ('md', 'html', None)
            reply_to: ID del mensaje al que responder
            
        Returns:
            Mensaje enviado o None si falló
        """
        try:
            target_chat = chat_id or self.config.chat_target
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado")
                return None
            
            message = await self.client.send_message(
                target_chat,
                text,
                parse_mode=parse_mode,
                reply_to=reply_to
            )
            
            self.logger.info(f"✅ Mensaje de texto enviado a {target_chat}")
            return message
            
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.send_text_message(text, chat_id, parse_mode, reply_to)
        except Exception as e:
            self.logger.error(f"❌ Error enviando mensaje de texto: {e}")
            return None
    
    async def reply_to_message(
        self,
        text: str,
        original_message_id: int,
        chat_id: Optional[int] = None,
        parse_mode: str = 'md'
    ) -> Optional[Any]:
        """
        Responder a un mensaje específico
        
        Args:
            text: Texto de la respuesta
            original_message_id: ID del mensaje al que responder
            chat_id: ID del chat específico (si no se especifica, usa el chat del mensaje original)
            parse_mode: Modo de parseo ('md', 'html', None)
            
        Returns:
            Mensaje enviado o None si falló
        """
        try:
            # Si no se especifica chat_id, buscar el chat del mensaje original
            if chat_id is None:
                # Buscar el mensaje original para obtener su chat
                try:
                    # Intentar en chat_target primero
                    if self.config.chat_target:
                        original_message = await self.client.get_messages(
                            self.config.chat_target, 
                            ids=original_message_id
                        )
                        if original_message:
                            target_chat = self.config.chat_target
                        else:
                            target_chat = None
                    else:
                        target_chat = None
                        
                    # Si no se encuentra, intentar en chat_me
                    if target_chat is None and self.config.chat_me:
                        original_message = await self.client.get_messages(
                            self.config.chat_me, 
                            ids=original_message_id
                        )
                        if original_message:
                            target_chat = self.config.chat_me
                        else:
                            target_chat = self.config.chat_target  # Fallback
                            
                except Exception as e:
                    self.logger.warning(f"No se pudo encontrar el mensaje original {original_message_id}: {e}")
                    target_chat = self.config.chat_target  # Fallback
            else:
                target_chat = chat_id
            
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado y no se pudo determinar el chat del mensaje original")
                return None
            
            message = await self.client.send_message(
                target_chat,
                text,
                parse_mode=parse_mode,
                reply_to=original_message_id
            )
            
            self.logger.info(f"↩️ Respuesta enviada a {target_chat} (reply to: {original_message_id})")
            return message
            
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.reply_to_message(text, original_message_id, chat_id, parse_mode)
        except Exception as e:
            self.logger.error(f"❌ Error enviando respuesta: {e}")
            await self.send_notification_to_me(text, parse_mode=parse_mode)
            return None
    
    async def edit_message(
        self,
        message_id: int,
        new_text: str,
        chat_id: Optional[int] = None,
        parse_mode: str = 'md'
    ) -> bool:
        """
        Editar un mensaje existente
        
        Args:
            message_id: ID del mensaje a editar
            new_text: Nuevo texto
            chat_id: ID del chat (usa chat_target por defecto)
            parse_mode: Modo de parseo
            
        Returns:
            True si se editó correctamente
        """
        try:
            target_chat = chat_id or self.config.chat_target
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado")
                return False
            
            await self.client.edit_message(
                target_chat,
                message_id,
                new_text,
                parse_mode=parse_mode
            )
            
            self.logger.debug(f"✅ Mensaje {message_id} editado en {target_chat}")
            return True
            
        except MessageNotModifiedError:
            self.logger.info("📝 Mensaje no modificado (contenido idéntico)")
            return True
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.edit_message(message_id, new_text, chat_id, parse_mode)
        except Exception as e:
            self.logger.error(f"❌ Error editando mensaje: {e}")
            return False
    
    async def send_photo(
        self,
        photo_path: Union[str, Path],
        caption: Optional[str] = None,
        chat_id: Optional[int] = None,
        parse_mode: str = 'md',
        reply_to: Optional[int] = None
    ) -> Optional[Any]:
        """
        Enviar imagen
        
        Args:
            photo_path: Ruta a la imagen
            caption: Texto del mensaje
            chat_id: ID del chat
            parse_mode: Modo de parseo
            reply_to: ID del mensaje al que responder
            
        Returns:
            Mensaje enviado o None si falló
        """
        try:
            target_chat = chat_id or self.config.chat_target
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado")
                return None
            
            if not os.path.exists(photo_path):
                self.logger.error(f"❌ Archivo no encontrado: {photo_path}")
                return None
            
            message = await self.client.send_file(
                target_chat,
                photo_path,
                caption=caption,
                parse_mode=parse_mode,
                reply_to=reply_to
            )
            
            self.logger.info(f"📸 Imagen enviada a {target_chat}: {photo_path}")
            return message
            
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.send_photo(photo_path, caption, chat_id, parse_mode, reply_to)
        except Exception as e:
            self.logger.error(f"❌ Error enviando imagen: {e}")
            return None
    
    async def send_video(
        self,
        video_path: Union[str, Path],
        caption: Optional[str] = None,
        chat_id: Optional[int] = None,
        parse_mode: str = 'md',
        reply_to: Optional[int] = None,
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        supports_streaming: bool = True
    ) -> Optional[Any]:
        """
        Enviar video
        
        Args:
            video_path: Ruta al video
            caption: Texto del mensaje
            chat_id: ID del chat
            parse_mode: Modo de parseo
            reply_to: ID del mensaje al que responder
            duration: Duración en segundos
            width: Ancho del video
            height: Alto del video
            supports_streaming: Si soporta streaming
            
        Returns:
            Mensaje enviado o None si falló
        """
        try:
            target_chat = chat_id or self.config.chat_target
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado")
                return None
            
            if not os.path.exists(video_path):
                self.logger.error(f"❌ Archivo no encontrado: {video_path}")
                return None
            
            message = await self.client.send_file(
                target_chat,
                video_path,
                caption=caption,
                parse_mode=parse_mode,
                reply_to=reply_to
            )
            
            self.logger.info(f"🎥 Video enviado a {target_chat}: {video_path}")
            return message
            
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.send_video(video_path, caption, chat_id, parse_mode, reply_to, duration, width, height, supports_streaming)
        except Exception as e:
            self.logger.error(f"❌ Error enviando video: {e}")
            return None
    
    async def send_animation(
        self,
        animation_path: Union[str, Path],
        caption: Optional[str] = None,
        chat_id: Optional[int] = None,
        parse_mode: str = 'md',
        reply_to: Optional[int] = None
    ) -> Optional[Any]:
        """
        Enviar animación/GIF
        
        Args:
            animation_path: Ruta a la animación
            caption: Texto del mensaje
            chat_id: ID del chat
            parse_mode: Modo de parseo
            reply_to: ID del mensaje al que responder
            
        Returns:
            Mensaje enviado o None si falló
        """
        try:
            target_chat = chat_id or self.config.chat_target
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado")
                return None
            
            if not os.path.exists(animation_path):
                self.logger.error(f"❌ Archivo no encontrado: {animation_path}")
                return None
            
            message = await self.client.send_file(
                target_chat,
                animation_path,
                caption=caption,
                parse_mode=parse_mode,
                reply_to=reply_to
            )
            
            self.logger.info(f"🎬 Animación enviada a {target_chat}: {animation_path}")
            return message
            
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.send_animation(animation_path, caption, chat_id, parse_mode, reply_to)
        except Exception as e:
            self.logger.error(f"❌ Error enviando animación: {e}")
            return None
    
    async def send_sticker(
        self,
        sticker_path: Union[str, Path],
        chat_id: Optional[int] = None,
        reply_to: Optional[int] = None
    ) -> Optional[Any]:
        """
        Enviar sticker
        
        Args:
            sticker_path: Ruta al sticker
            chat_id: ID del chat
            reply_to: ID del mensaje al que responder
            
        Returns:
            Mensaje enviado o None si falló
        """
        try:
            target_chat = chat_id or self.config.chat_target
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado")
                return None
            
            if not os.path.exists(sticker_path):
                self.logger.error(f"❌ Archivo no encontrado: {sticker_path}")
                return None
            
            message = await self.client.send_file(
                target_chat,
                sticker_path,
                reply_to=reply_to
            )
            
            self.logger.info(f"🔖 Sticker enviado a {target_chat}: {sticker_path}")
            return message
            
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.send_sticker(sticker_path, chat_id, reply_to)
        except Exception as e:
            self.logger.error(f"❌ Error enviando sticker: {e}")
            return None
    
    async def send_document(
        self,
        document_path: Union[str, Path],
        caption: Optional[str] = None,
        chat_id: Optional[int] = None,
        parse_mode: str = 'md',
        reply_to: Optional[int] = None,
        force_document: bool = True
    ) -> Optional[Any]:
        """
        Enviar documento
        
        Args:
            document_path: Ruta al documento
            caption: Texto del mensaje
            chat_id: ID del chat
            parse_mode: Modo de parseo
            reply_to: ID del mensaje al que responder
            force_document: Forzar como documento (no como imagen/video)
            
        Returns:
            Mensaje enviado o None si falló
        """
        try:
            target_chat = chat_id or self.config.chat_target
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado")
                return None
            
            if not os.path.exists(document_path):
                self.logger.error(f"❌ Archivo no encontrado: {document_path}")
                return None
            
            message = await self.client.send_file(
                target_chat,
                document_path,
                caption=caption,
                parse_mode=parse_mode,
                reply_to=reply_to,
                force_document=force_document
            )
            
            self.logger.info(f"📄 Documento enviado a {target_chat}: {document_path}")
            return message
            
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.send_document(document_path, caption, chat_id, parse_mode, reply_to, force_document)
        except Exception as e:
            self.logger.error(f"❌ Error enviando documento: {e}")
            return None
    
    async def send_album(
        self,
        file_paths: List[Union[str, Path]],
        caption: Optional[str] = None,
        chat_id: Optional[int] = None,
        parse_mode: str = 'md',
        reply_to: Optional[int] = None
    ) -> Optional[List[Any]]:
        """
        Enviar álbum de multimedia (hasta 10 archivos)
        
        Args:
            file_paths: Lista de rutas a los archivos
            caption: Texto del mensaje (solo en el primer archivo)
            chat_id: ID del chat
            parse_mode: Modo de parseo
            reply_to: ID del mensaje al que responder
            
        Returns:
            Lista de mensajes enviados o None si falló
        """
        try:
            target_chat = chat_id or self.config.chat_target
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado")
                return None
            
            if not file_paths:
                self.logger.error("❌ Lista de archivos vacía")
                return None
            
            if len(file_paths) > 10:
                self.logger.warning("⚠️ Telegram permite máximo 10 archivos por álbum")
                file_paths = file_paths[:10]
            
            # Verificar que todos los archivos existen
            valid_files = []
            for file_path in file_paths:
                if os.path.exists(file_path):
                    valid_files.append(file_path)
                else:
                    self.logger.warning(f"⚠️ Archivo no encontrado: {file_path}")
            
            if not valid_files:
                self.logger.error("❌ No hay archivos válidos para enviar")
                return None
            
            # Enviar álbum
            messages = await self.client.send_file(
                target_chat,
                valid_files,
                caption=caption,
                parse_mode=parse_mode,
                reply_to=reply_to
            )
            
            self.logger.info(f"📚 Álbum enviado a {target_chat}: {len(valid_files)} archivos")
            return messages if isinstance(messages, list) else [messages]
            
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.send_album(file_paths, caption, chat_id, parse_mode, reply_to)
        except Exception as e:
            self.logger.error(f"❌ Error enviando álbum: {e}")
            return None
    
    async def send_notification_to_me(
        self,
        message: str,
        parse_mode: str = 'md'
    ) -> Optional[Any]:
        """
        Enviar notificación al chat personal (CHAT_ME)
        
        Args:
            message: Mensaje de notificación
            parse_mode: Modo de parseo
            
        Returns:
            Mensaje enviado o None si falló
        """
        try:
            if not self.config.chat_me:
                self.logger.error("❌ CHAT_ME no configurado")
                return None
            
            mensaje = await self.send_text_message(
                message,
                chat_id=self.config.chat_me,
                parse_mode=parse_mode
            )
            self.logger.info(f"Mensaje de notificación enviado a CHAT_ME: {mensaje.id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando notificación: {e}")
            return None
        
        return mensaje
    
    async def delete_message(
        self,
        message_id: int,
        chat_id: Optional[int] = None
    ) -> bool:
        """
        Eliminar un mensaje
        
        Args:
            message_id: ID del mensaje a eliminar
            chat_id: ID del chat (usa chat_target por defecto)
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            target_chat = chat_id or self.config.chat_target
            if not target_chat:
                self.logger.error("No hay chat objetivo configurado")
                return False
            
            await self.client.delete_messages(target_chat, message_id)
            
            self.logger.info(f"🗑️ Mensaje {message_id} eliminado de {target_chat}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error eliminando mensaje: {e}")
            return False
    
    async def download_media_from_message(
        self,
        message: Any,
        download_dir: Optional[Union[str, Path]] = None,
        progress_callback: Optional[callable] = None,
        file_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Descargar multimedia de un mensaje sin importar el tamaño
        
        Args:
            message: Mensaje de Telegram que contiene multimedia
            download_dir: Directorio donde descargar (usa /app/downloads por defecto)
            progress_callback: Función opcional para reportar progreso
            file_name: Nombre personalizado para el archivo (opcional)
            
        Returns:
            Ruta del archivo descargado o None si falló
        """
        try:
            if not message.media:
                self.logger.warning("⚠️ El mensaje no contiene multimedia")
                return None
            
            # Determinar directorio de descarga
            target_dir = Path(download_dir) if download_dir else Path('/app/downloads')
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre único para el archivo
            if file_name:
                # Usar nombre proporcionado, manejar conflictos con sufijos numéricos
                base_name = Path(file_name).stem
                extension = Path(file_name).suffix or self._get_media_extension(message.media)
                
                # Verificar si el archivo ya existe y añadir sufijo si es necesario
                counter = 0
                while True:
                    if counter == 0:
                        candidate_name = f"{base_name}{extension}"
                    else:
                        candidate_name = f"{base_name} ({counter}){extension}"
                    
                    file_path = target_dir / candidate_name
                    if not file_path.exists():
                        file_name = candidate_name
                        break
                    counter += 1
            else:
                # Generar nombre automático
                timestamp = asyncio.get_event_loop().time()
                base_name = f"media_{message.id}_{int(timestamp)}"
                file_extension = self._get_media_extension(message.media)
                file_name = f"{base_name}{file_extension}"
                file_path = target_dir / file_name
            
            self.logger.info(f"📥 Descargando multimedia: {file_name}")
            
            # Descargar el archivo
            downloaded_path = await self.client.download_media(
                message.media,
                file=str(file_path),
                progress_callback=progress_callback
            )
            
            if downloaded_path:
                self.logger.info(f"✅ Multimedia descargada: {downloaded_path}")
                return str(downloaded_path)
            else:
                self.logger.error("❌ Falló la descarga de multimedia")
                return None
                
        except FloodWaitError as e:
            self.logger.warning(f"⏰ FloodWait: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.download_media_from_message(message, download_dir, progress_callback)
        except Exception as e:
            self.logger.error(f"❌ Error descargando multimedia: {e}")
            return None
    
    def _get_media_extension(self, media) -> str:
        """
        Determinar extensión de archivo basada en el tipo de media
        
        Args:
            media: Objeto media de Telegram
            
        Returns:
            Extensión del archivo con punto (ej: '.jpg', '.mp4')
        """
        if isinstance(media, MessageMediaPhoto):
            return '.jpg'
        elif isinstance(media, MessageMediaDocument):
            document = media.document
            if document.mime_type:
                # Mapear tipos MIME comunes a extensiones
                mime_to_ext = {
                    'video/mp4': '.mp4',
                    'video/avi': '.avi',
                    'video/mov': '.mov',
                    'video/mkv': '.mkv',
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'image/webp': '.webp',
                    'audio/mp3': '.mp3',
                    'audio/wav': '.wav',
                    'audio/ogg': '.ogg',
                    'application/pdf': '.pdf',
                    'application/zip': '.zip',
                    'text/plain': '.txt'
                }
                return mime_to_ext.get(document.mime_type, '.bin')
            
            # Si no hay MIME type, intentar por atributos del documento
            for attr in document.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    # Extraer extensión del nombre del archivo
                    file_name = attr.file_name
                    if '.' in file_name:
                        return '.' + file_name.split('.')[-1].lower()
        
        # Extensión por defecto
        return '.bin'
    
    def get_chat_info(self) -> Dict[str, Any]:
        """
        Obtener información de configuración de chats
        
        Returns:
            Diccionario con información de chats
        """
        return {
            'chat_me': self.config.chat_me,
            'chat_target': self.config.chat_target,
            'has_chat_me': bool(self.config.chat_me),
            'has_chat_target': bool(self.config.chat_target)
        }