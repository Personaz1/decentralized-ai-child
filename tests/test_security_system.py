import pytest
import asyncio
from pathlib import Path
from datetime import datetime
from src.core.security_system import SecuritySystem

@pytest.fixture
async def security_system(test_root, test_logger, test_config):
    """Создание экземпляра SecuritySystem для тестов"""
    system = SecuritySystem(
        system_root=test_root,
        logger=test_logger,
        config=test_config
    )
    await system.initialize()
    return system

@pytest.mark.asyncio
async def test_initialization(security_system):
    """Тест инициализации системы"""
    assert security_system.backup_dir is not None
    assert security_system.backup_dir.exists()
    assert security_system.security_history is not None
    assert security_system.backup_history is not None

@pytest.mark.asyncio
async def test_validate_security(security_system):
    """Тест валидации безопасности"""
    # Тест безопасного кода
    safe_code = """
def safe_function(a: int, b: int) -> int:
    return a + b
    """
    result = await security_system.validate_security(safe_code)
    assert result["is_safe"]
    
    # Тест опасного кода
    dangerous_code = """
import os
os.system('rm -rf /')
    """
    result = await security_system.validate_security(dangerous_code)
    assert not result["is_safe"]
    assert "dangerous_patterns" in result["issues"]

@pytest.mark.asyncio
async def test_backup_creation(security_system):
    """Тест создания бэкапа"""
    test_files = {
        "test1.py": "print('test1')",
        "test2.py": "print('test2')"
    }
    
    backup_info = await security_system.create_backup(test_files)
    
    assert backup_info["success"]
    assert backup_info["backup_path"].exists()
    assert len(list(backup_info["backup_path"].glob("*.py"))) == 2
    
    # Проверяем содержимое файлов
    for file_name, content in test_files.items():
        backup_file = backup_info["backup_path"] / file_name
        assert backup_file.read_text() == content

@pytest.mark.asyncio
async def test_backup_restoration(security_system):
    """Тест восстановления бэкапа"""
    # Создаем тестовые файлы
    test_files = {
        "test1.py": "print('test1')",
        "test2.py": "print('test2')"
    }
    
    # Создаем бэкап
    backup_info = await security_system.create_backup(test_files)
    
    # Изменяем оригинальные файлы
    for file_name, content in test_files.items():
        file_path = security_system.system_root / file_name
        file_path.write_text("modified content")
    
    # Восстанавливаем бэкап
    restore_result = await security_system.restore_backup(backup_info["backup_path"])
    
    assert restore_result["success"]
    
    # Проверяем восстановленные файлы
    for file_name, original_content in test_files.items():
        restored_file = security_system.system_root / file_name
        assert restored_file.read_text() == original_content

@pytest.mark.asyncio
async def test_dangerous_patterns(security_system):
    """Тест проверки опасных паттернов"""
    dangerous_patterns = [
        "eval('1+1')",
        "exec('print(1)')",
        "os.system('ls')",
        "subprocess.call(['ls'])",
        "pickle.loads(data)",
        "yaml.load(data)",
        "json.loads(data)",
        "marshal.loads(data)",
        "base64.b64decode(data)"
    ]
    
    for pattern in dangerous_patterns:
        result = await security_system._check_dangerous_patterns(pattern)
        assert result["is_dangerous"]
        assert len(result["patterns"]) > 0

@pytest.mark.asyncio
async def test_dependencies_check(security_system):
    """Тест проверки зависимостей"""
    # Тест безопасных зависимостей
    safe_imports = """
import math
import random
import datetime
    """
    result = await security_system._check_dependencies(safe_imports)
    assert result["is_safe"]
    
    # Тест подозрительных зависимостей
    suspicious_imports = """
import cryptography
import paramiko
import requests
    """
    result = await security_system._check_dependencies(suspicious_imports)
    assert not result["is_safe"]
    assert len(result["suspicious_deps"]) > 0

@pytest.mark.asyncio
async def test_file_permissions(security_system):
    """Тест проверки прав доступа"""
    test_file = security_system.system_root / "test.py"
    test_file.write_text("test content")
    
    # Проверяем права на чтение
    result = await security_system._check_permissions(test_file, "read")
    assert result["has_permission"]
    
    # Проверяем права на запись
    result = await security_system._check_permissions(test_file, "write")
    assert result["has_permission"]
    
    # Проверяем права на выполнение
    result = await security_system._check_permissions(test_file, "execute")
    assert not result["has_permission"]  # По умолчанию нет прав на выполнение

@pytest.mark.asyncio
async def test_file_integrity(security_system):
    """Тест проверки целостности файлов"""
    test_file = security_system.system_root / "test.py"
    original_content = "test content"
    test_file.write_text(original_content)
    
    # Получаем хэш файла
    original_hash = await security_system._calculate_file_hash(test_file)
    
    # Проверяем целостность
    result = await security_system._check_integrity(test_file, original_hash)
    assert result["is_valid"]
    
    # Модифицируем файл
    test_file.write_text("modified content")
    
    # Проверяем целостность снова
    result = await security_system._check_integrity(test_file, original_hash)
    assert not result["is_valid"]

@pytest.mark.asyncio
async def test_security_history(security_system):
    """Тест истории безопасности"""
    # Выполняем несколько проверок
    await security_system.validate_security("print('test')")
    await security_system.validate_security("import os; os.system('ls')")
    
    history = security_system.get_security_history()
    assert len(history) >= 2
    assert "timestamp" in history[0]
    assert "result" in history[0]
    assert "details" in history[0] 