#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de base de datos
"""

import sys
import os
sys.path.append('/app')

from src.database import DatabaseManager, Message, User, Chat
from datetime import datetime

def test_database():
    """Probar el sistema de base de datos"""
    
    print("🔄 Inicializando base de datos...")
    db = DatabaseManager("data/test_bot.db")
    
    print("✅ Base de datos inicializada")
    
    # Crear usuario de prueba
    user = User(
        user_id=12345,
        username="test_user",
        first_name="Usuario",
        last_name="Prueba",
        is_bot=False,
        language_code="es"
    )
    
    print("💾 Guardando usuario de prueba...")
    success = db.save_user(user)
    print(f"Usuario guardado: {'✅' if success else '❌'}")
    
    # Crear chat de prueba
    chat = Chat(
        chat_id=-123456,
        title="Chat de Prueba",
        chat_type="group",
        username="test_chat",
        description="Un chat para pruebas"
    )
    
    print("💾 Guardando chat de prueba...")
    success = db.save_chat(chat)
    print(f"Chat guardado: {'✅' if success else '❌'}")
    
    # Crear mensaje de prueba
    message = Message(
        message_id=1001,
        chat_id=-123456,
        user_id=12345,
        text="Este es un mensaje de prueba",
        message_type="text",
        created_at=datetime.now()
    )
    
    print("💾 Guardando mensaje de prueba...")
    success = db.save_message(message)
    print(f"Mensaje guardado: {'✅' if success else '❌'}")
    
    # Obtener estadísticas
    print("📊 Obteniendo estadísticas...")
    stats = db.get_message_stats()
    print(f"Total de mensajes: {stats.get('total_messages', 0)}")
    print(f"Tipos de mensaje: {stats.get('by_type', {})}")
    
    print("✅ Prueba de base de datos completada exitosamente")

if __name__ == "__main__":
    test_database()