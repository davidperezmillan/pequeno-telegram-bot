"""
Modelos de datos para la base de datos del bot
"""

from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime
import json


@dataclass
class User:
    """Modelo para representar un usuario de Telegram"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_bot: bool = False
    language_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para almacenamiento"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_bot': self.is_bot,
            'language_code': self.language_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Crear instancia desde diccionario"""
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        
        return cls(
            user_id=data['user_id'],
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            is_bot=data.get('is_bot', False),
            language_code=data.get('language_code'),
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class Chat:
    """Modelo para representar un chat de Telegram"""
    chat_id: int
    title: Optional[str] = None
    chat_type: Optional[str] = None  # 'private', 'group', 'supergroup', 'channel'
    username: Optional[str] = None
    description: Optional[str] = None
    member_count: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para almacenamiento"""
        return {
            'chat_id': self.chat_id,
            'title': self.title,
            'chat_type': self.chat_type,
            'username': self.username,
            'description': self.description,
            'member_count': self.member_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Chat':
        """Crear instancia desde diccionario"""
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        
        return cls(
            chat_id=data['chat_id'],
            title=data.get('title'),
            chat_type=data.get('chat_type'),
            username=data.get('username'),
            description=data.get('description'),
            member_count=data.get('member_count'),
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class Message:
    """Modelo para representar un mensaje de Telegram"""
    message_id: int
    chat_id: int
    user_id: int
    text: Optional[str] = None
    message_type: str = 'text'  # 'text', 'photo', 'video', 'document', 'sticker', etc.
    media_info: Optional[dict] = None  # Información adicional sobre media
    reply_to_message_id: Optional[int] = None
    forward_from_chat_id: Optional[int] = None
    forward_from_message_id: Optional[int] = None
    edit_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    raw_data: Optional[str] = None  # JSON completo del mensaje original
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para almacenamiento"""
        return {
            'message_id': self.message_id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'text': self.text,
            'message_type': self.message_type,
            'media_info': json.dumps(self.media_info) if self.media_info else None,
            'reply_to_message_id': self.reply_to_message_id,
            'forward_from_chat_id': self.forward_from_chat_id,
            'forward_from_message_id': self.forward_from_message_id,
            'edit_date': self.edit_date.isoformat() if self.edit_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'raw_data': self.raw_data
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Crear instancia desde diccionario"""
        edit_date = datetime.fromisoformat(data['edit_date']) if data.get('edit_date') else None
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        media_info = json.loads(data['media_info']) if data.get('media_info') else None
        
        return cls(
            message_id=data['message_id'],
            chat_id=data['chat_id'],
            user_id=data['user_id'],
            text=data.get('text'),
            message_type=data.get('message_type', 'text'),
            media_info=media_info,
            reply_to_message_id=data.get('reply_to_message_id'),
            forward_from_chat_id=data.get('forward_from_chat_id'),
            forward_from_message_id=data.get('forward_from_message_id'),
            edit_date=edit_date,
            created_at=created_at,
            raw_data=data.get('raw_data')
        )
    
    @classmethod
    def from_telethon_message(cls, event, raw_data: str = None) -> 'Message':
        """Crear instancia desde un evento de Telethon"""
        message = event.message
        
        # Determinar tipo de mensaje
        message_type = 'text'
        media_info = None
        
        if message.media:
            if message.photo:
                message_type = 'photo'
                media_info = {'has_photo': True}
            elif message.video:
                message_type = 'video'
                media_info = {
                    'duration': getattr(message.video, 'duration', None),
                    'width': getattr(message.video, 'w', None),
                    'height': getattr(message.video, 'h', None)
                }
            elif message.document:
                message_type = 'document'
                media_info = {
                    'file_name': getattr(message.document, 'file_name', None),
                    'size': getattr(message.document, 'size', None)
                }
            elif message.sticker:
                message_type = 'sticker'
                media_info = {'sticker': True}
            else:
                message_type = 'media'
                media_info = {'media_type': str(type(message.media).__name__)}
        
        return cls(
            message_id=message.id,
            chat_id=event.chat_id,
            user_id=event.sender_id,
            text=message.text,
            message_type=message_type,
            media_info=media_info,
            reply_to_message_id=getattr(message, 'reply_to_msg_id', None),
            forward_from_chat_id=getattr(message.forward, 'from_id', None) if message.forward else None,
            forward_from_message_id=getattr(message.forward, 'channel_post', None) if message.forward else None,
            edit_date=message.edit_date,
            created_at=message.date,
            raw_data=raw_data
        )