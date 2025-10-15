#!/usr/bin/env python3
"""
Test básico de la clase FileManager
"""

import sys
import os
sys.path.append('.')

from src.utils.file_manager import FileManager

def test_file_manager():
    """Test básico de inicialización y métodos"""
    print("🧪 Probando FileManager...")

    # Crear instancia
    fm = FileManager()
    print("✅ Instancia creada correctamente")

    # Verificar que los métodos existen
    assert hasattr(fm, 'get_video_duration'), "Método get_video_duration no encontrado"
    assert hasattr(fm, 'calculate_random_start_time'), "Método calculate_random_start_time no encontrado"
    assert hasattr(fm, 'create_random_video_clip'), "Método create_random_video_clip no encontrado"
    assert hasattr(fm, 'cleanup_files'), "Método cleanup_files no encontrado"
    assert hasattr(fm, 'get_file_info'), "Método get_file_info no encontrado"
    print("✅ Todos los métodos están presentes")

    # Probar cálculo de tiempo aleatorio
    random_time = fm.calculate_random_start_time(120.0, 30)
    assert isinstance(random_time, int), "calculate_random_start_time debe retornar int"
    assert 0 <= random_time <= 90, f"Tiempo aleatorio fuera de rango: {random_time}"
    print(f"✅ Cálculo de tiempo aleatorio funciona: {random_time}s")

    # Probar get_file_info con archivo inexistente
    info = fm.get_file_info("/archivo/inexistente.mp4")
    assert info is None, "get_file_info debe retornar None para archivos inexistentes"
    print("✅ get_file_info maneja archivos inexistentes correctamente")

    print("🎉 Todos los tests pasaron exitosamente!")

if __name__ == "__main__":
    test_file_manager()