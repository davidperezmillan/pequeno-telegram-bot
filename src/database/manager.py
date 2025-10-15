"""
Gestor de base de datos para el bot de Telegram
"""

import sqlite3
import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager

from .models import Message, User, Chat
from ..config import setup_logger


class DatabaseManager:
    """Gestor principal de la base de datos SQLite"""
    
    def __init__(self, db_path: str = "data/bot_data.db"):
        """
        Inicializar el gestor de base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.logger = setup_logger('database_manager')
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Inicializar base de datos
        self._init_database()
        
        self.logger.info(f"Base de datos inicializada en: {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error en operación de base de datos: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Inicializar las tablas de la base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_bot BOOLEAN DEFAULT FALSE,
                    language_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de chats
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    title TEXT,
                    chat_type TEXT,
                    username TEXT,
                    description TEXT,
                    member_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de mensajes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    chat_id INTEGER,
                    user_id INTEGER,
                    text TEXT,
                    message_type TEXT DEFAULT 'text',
                    media_info TEXT,
                    reply_to_message_id INTEGER,
                    forward_from_chat_id INTEGER,
                    forward_from_message_id INTEGER,
                    edit_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (chat_id) REFERENCES chats (chat_id),
                    UNIQUE(message_id, chat_id)
                )
            """)
            
            # Índices para mejorar rendimiento
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages (chat_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages (created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_message_type ON messages (message_type)")
            
            conn.commit()
            self.logger.info("Tablas de base de datos creadas correctamente")
    
    # MÉTODOS PARA USUARIOS
    def save_user(self, user: User) -> bool:
        """
        Guardar o actualizar un usuario
        
        Args:
            user: Instancia de User
            
        Returns:
            True si se guardó correctamente
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si el usuario existe
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.user_id,))
                exists = cursor.fetchone()
                
                now = datetime.now()
                
                if exists:
                    # Actualizar usuario existente
                    cursor.execute("""
                        UPDATE users SET
                            username = ?, first_name = ?, last_name = ?,
                            is_bot = ?, language_code = ?, updated_at = ?
                        WHERE user_id = ?
                    """, (
                        user.username, user.first_name, user.last_name,
                        user.is_bot, user.language_code, now, user.user_id
                    ))
                else:
                    # Insertar nuevo usuario
                    cursor.execute("""
                        INSERT INTO users (
                            user_id, username, first_name, last_name,
                            is_bot, language_code, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user.user_id, user.username, user.first_name, user.last_name,
                        user.is_bot, user.language_code, now, now
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error guardando usuario {user.user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Obtener un usuario por ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return User.from_dict(dict(row))
                return None
                
        except Exception as e:
            self.logger.error(f"Error obteniendo usuario {user_id}: {e}")
            return None
    
    # MÉTODOS PARA CHATS
    def save_chat(self, chat: Chat) -> bool:
        """
        Guardar o actualizar un chat
        
        Args:
            chat: Instancia de Chat
            
        Returns:
            True si se guardó correctamente
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si el chat existe
                cursor.execute("SELECT chat_id FROM chats WHERE chat_id = ?", (chat.chat_id,))
                exists = cursor.fetchone()
                
                now = datetime.now()
                
                if exists:
                    # Actualizar chat existente
                    cursor.execute("""
                        UPDATE chats SET
                            title = ?, chat_type = ?, username = ?, description = ?,
                            member_count = ?, updated_at = ?
                        WHERE chat_id = ?
                    """, (
                        chat.title, chat.chat_type, chat.username, chat.description,
                        chat.member_count, now, chat.chat_id
                    ))
                else:
                    # Insertar nuevo chat
                    cursor.execute("""
                        INSERT INTO chats (
                            chat_id, title, chat_type, username, description,
                            member_count, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        chat.chat_id, chat.title, chat.chat_type, chat.username,
                        chat.description, chat.member_count, now, now
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error guardando chat {chat.chat_id}: {e}")
            return False
    
    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Obtener un chat por ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,))
                row = cursor.fetchone()
                
                if row:
                    return Chat.from_dict(dict(row))
                return None
                
        except Exception as e:
            self.logger.error(f"Error obteniendo chat {chat_id}: {e}")
            return None
    
    # MÉTODOS PARA MENSAJES
    def save_message(self, message: Message) -> bool:
        """
        Guardar un mensaje
        
        Args:
            message: Instancia de Message
            
        Returns:
            True si se guardó correctamente
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO messages (
                        message_id, chat_id, user_id, text, message_type,
                        media_info, reply_to_message_id, forward_from_chat_id,
                        forward_from_message_id, edit_date, created_at, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.message_id, message.chat_id, message.user_id,
                    message.text, message.message_type,
                    json.dumps(message.media_info) if message.media_info else None,
                    message.reply_to_message_id, message.forward_from_chat_id,
                    message.forward_from_message_id, message.edit_date,
                    message.created_at, message.raw_data
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error guardando mensaje {message.message_id}: {e}")
            return False
    
    def get_messages_by_chat(self, chat_id: int, limit: int = 100, offset: int = 0) -> List[Message]:
        """Obtener mensajes de un chat específico"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE chat_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """, (chat_id, limit, offset))
                
                rows = cursor.fetchall()
                return [Message.from_dict(dict(row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Error obteniendo mensajes del chat {chat_id}: {e}")
            return []
    
    def get_message(self, message_id: int, chat_id: int) -> Optional[Message]:
        """
        Obtener un mensaje específico por ID y chat
        
        Args:
            message_id: ID del mensaje
            chat_id: ID del chat
            
        Returns:
            Instancia de Message o None si no existe
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM messages WHERE message_id = ? AND chat_id = ?", (message_id, chat_id))
                row = cursor.fetchone()
                
                if row:
                    return Message.from_dict(dict(row))
                return None
                
        except Exception as e:
            self.logger.error(f"Error obteniendo mensaje {message_id} en chat {chat_id}: {e}")
            return None
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de mensajes"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total de mensajes
                cursor.execute("SELECT COUNT(*) as total FROM messages")
                total = cursor.fetchone()['total']
                
                # Mensajes por tipo
                cursor.execute("""
                    SELECT message_type, COUNT(*) as count 
                    FROM messages 
                    GROUP BY message_type 
                    ORDER BY count DESC
                """)
                by_type = dict(cursor.fetchall())
                
                # Mensajes por chat (top 10)
                cursor.execute("""
                    SELECT c.title, c.chat_id, COUNT(*) as count
                    FROM messages m
                    JOIN chats c ON m.chat_id = c.chat_id
                    GROUP BY m.chat_id
                    ORDER BY count DESC
                    LIMIT 10
                """)
                by_chat = [dict(row) for row in cursor.fetchall()]
                
                # Mensajes por día (últimos 7 días)
                cursor.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM messages
                    WHERE created_at >= datetime('now', '-7 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """)
                by_day = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'total_messages': total,
                    'by_type': by_type,
                    'top_chats': by_chat,
                    'last_7_days': by_day
                }
                
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def process_telethon_event(self, event) -> bool:
        """
        Procesar un evento de Telethon y guardar toda la información
        
        Args:
            event: Evento de Telethon (NewMessage o MessageEdited)
            
        Returns:
            True si se procesó correctamente
        """
        try:
            # Obtener información del remitente
            sender = event.sender
            if sender:
                user = User(
                    user_id=sender.id,
                    username=getattr(sender, 'username', None),
                    first_name=getattr(sender, 'first_name', None),
                    last_name=getattr(sender, 'last_name', None),
                    is_bot=getattr(sender, 'bot', False),
                    language_code=getattr(sender, 'lang_code', None)
                )
                self.save_user(user)
            
            # Obtener información del chat
            chat_entity = event.chat
            if chat_entity:
                chat = Chat(
                    chat_id=event.chat_id,
                    title=getattr(chat_entity, 'title', None),
                    chat_type=getattr(chat_entity, 'type', 'private'),
                    username=getattr(chat_entity, 'username', None),
                    description=getattr(chat_entity, 'about', None),
                    member_count=getattr(chat_entity, 'participants_count', None)
                )
                self.save_chat(chat)
            
            # Guardar el mensaje
            raw_data = json.dumps(event.message.to_dict(), default=str)
            message = Message.from_telethon_message(event, raw_data)
            success = self.save_message(message)
            
            if success:
                self.logger.info(f"Mensaje {message.message_id} guardado en la base de datos")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error procesando evento de Telethon: {e}")
            return False