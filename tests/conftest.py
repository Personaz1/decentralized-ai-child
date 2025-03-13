import pytest
import logging
from pathlib import Path
import tempfile
import shutil
import os

@pytest.fixture(scope="session")
def test_root():
    """Создание временной директории для тестов"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="session")
def test_logger():
    """Настройка логгера для тестов"""
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    
    # Создаем директорию для логов
    log_dir = Path("test_logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настраиваем файловый handler
    file_handler = logging.FileHandler(log_dir / "test.log")
    file_handler.setLevel(logging.DEBUG)
    
    # Настраиваем консольный handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Добавляем handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

@pytest.fixture(scope="session")
def test_config():
    """Создание тестовой конфигурации"""
    return {
        "system": {
            "name": "TestSystem",
            "version": "1.0.0",
            "min_nodes": 1,
            "max_nodes": 3,
            "log_level": "DEBUG",
            "data_dir": "test_data",
            "temp_dir": "test_temp"
        },
        "monitoring": {
            "performance_interval": 1,
            "alert_thresholds": {
                "cpu": 80,
                "memory": 80,
                "disk": 80
            }
        },
        "network": {
            "optimization_interval": 1,
            "connection_timeout": 5,
            "retry_attempts": 3
        },
        "knowledge_exchange": {
            "model_update_interval": 1,
            "min_confidence": 0.7,
            "max_models": 5
        },
        "evolution": {
            "population_size": 5,
            "mutation_rate": 0.1,
            "crossover_rate": 0.7,
            "elite_size": 1,
            "generations": 3
        },
        "self_reflection": {
            "interval": 1,
            "analysis_depth": "basic",
            "improvement_threshold": 0.1
        },
        "testing": {
            "interval": 1,
            "coverage_threshold": 0.5,
            "test_types": ["unit", "integration"]
        },
        "code_analysis": {
            "interval": 1,
            "analysis_depth": "basic",
            "sources": ["local"]
        },
        "validation": {
            "interval": 1,
            "validation_levels": ["syntax", "security", "performance"],
            "max_validation_time": 10
        },
        "security": {
            "backup_enabled": True,
            "backup_retention_days": 1,
            "max_backups": 3,
            "validation_checks": ["dangerous_patterns", "dependencies", "permissions", "integrity"],
            "suspicious_dependencies": ["cryptography", "paramiko", "requests"],
            "dangerous_patterns": [
                "eval\\(",
                "exec\\(",
                "os\\.system\\(",
                "subprocess\\.call\\(",
                "subprocess\\.Popen\\(",
                "pickle\\.loads\\(",
                "yaml\\.load\\(",
                "json\\.loads\\(",
                "marshal\\.loads\\(",
                "base64\\.b64decode\\("
            ],
            "permissions": {
                "read": ["r", "rb"],
                "write": ["w", "wb", "a", "ab"],
                "execute": ["x"]
            },
            "integrity_check": {
                "enabled": True,
                "hash_algorithm": "sha256"
            }
        }
    }

@pytest.fixture(scope="session")
def test_models_dir(test_root):
    """Создание директории для тестовых моделей"""
    models_dir = test_root / "models"
    models_dir.mkdir(exist_ok=True)
    return models_dir

@pytest.fixture(scope="session")
def test_cache_dir(test_root):
    """Создание директории для тестового кэша"""
    cache_dir = test_root / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir 