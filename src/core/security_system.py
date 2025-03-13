from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import ast
import re
from datetime import datetime
import hashlib
import shutil
import json

class SecuritySystem:
    def __init__(self, system_root: Path):
        self.system_root = system_root
        self.logger = logging.getLogger(__name__)
        self.security_history = []
        self.backup_dir = system_root / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    async def validate_security(self, changes: Dict[str, Any]) -> bool:
        """Проверка безопасности изменений"""
        try:
            # Проверяем опасные паттерны
            if not self._check_dangerous_patterns(changes):
                return False
                
            # Проверяем зависимости
            if not self._check_dependencies(changes):
                return False
                
            # Проверяем права доступа
            if not self._check_permissions(changes):
                return False
                
            # Проверяем целостность
            if not self._check_integrity(changes):
                return False
                
            # Сохраняем историю проверок
            self.security_history.append({
                "timestamp": datetime.now().isoformat(),
                "changes": changes,
                "status": "success"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки безопасности: {e}")
            self.security_history.append({
                "timestamp": datetime.now().isoformat(),
                "changes": changes,
                "status": "error",
                "error": str(e)
            })
            return False
            
    def _check_dangerous_patterns(self, changes: Dict[str, Any]) -> bool:
        """Проверка опасных паттернов"""
        dangerous_patterns = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"os\.system\s*\(",
            r"subprocess\.call\s*\(",
            r"subprocess\.Popen\s*\(",
            r"__import__\s*\(",
            r"open\s*\([^)]*\)",
            r"file\s*\([^)]*\)",
            r"input\s*\(",
            r"raw_input\s*\("
        ]
        
        for file_path, content in changes.items():
            for pattern in dangerous_patterns:
                if re.search(pattern, content):
                    self.logger.warning(f"Обнаружен опасный паттерн в {file_path}: {pattern}")
                    return False
                    
        return True
        
    def _check_dependencies(self, changes: Dict[str, Any]) -> bool:
        """Проверка зависимостей"""
        for file_path, content in changes.items():
            try:
                tree = ast.parse(content)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(node.module)
                        
                # Проверяем подозрительные зависимости
                suspicious_deps = [
                    "cryptography",
                    "paramiko",
                    "requests",
                    "urllib",
                    "socket",
                    "subprocess",
                    "os",
                    "sys"
                ]
                
                for dep in imports:
                    if dep in suspicious_deps:
                        self.logger.warning(f"Обнаружена подозрительная зависимость в {file_path}: {dep}")
                        return False
                        
            except Exception as e:
                self.logger.error(f"Ошибка проверки зависимостей в {file_path}: {e}")
                return False
                
        return True
        
    def _check_permissions(self, changes: Dict[str, Any]) -> bool:
        """Проверка прав доступа"""
        for file_path in changes:
            path = Path(file_path)
            if not path.exists():
                continue
                
            # Проверяем права на чтение
            if not os.access(path, os.R_OK):
                self.logger.warning(f"Нет прав на чтение файла {file_path}")
                return False
                
            # Проверяем права на запись
            if not os.access(path, os.W_OK):
                self.logger.warning(f"Нет прав на запись файла {file_path}")
                return False
                
        return True
        
    def _check_integrity(self, changes: Dict[str, Any]) -> bool:
        """Проверка целостности"""
        for file_path, content in changes.items():
            path = Path(file_path)
            if not path.exists():
                continue
                
            # Проверяем хеш файла
            current_hash = self._calculate_file_hash(path)
            new_hash = self._calculate_content_hash(content)
            
            if current_hash != new_hash:
                self.logger.warning(f"Нарушена целостность файла {file_path}")
                return False
                
        return True
        
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Расчет хеша файла"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
        
    def _calculate_content_hash(self, content: str) -> str:
        """Расчет хеша содержимого"""
        return hashlib.sha256(content.encode()).hexdigest()
        
    async def create_backup(self, changes: Dict[str, Any]) -> bool:
        """Создание резервной копии"""
        try:
            # Создаем директорию для бэкапа
            backup_path = self.backup_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path.mkdir(exist_ok=True)
            
            # Копируем файлы
            for file_path in changes:
                src = Path(file_path)
                if src.exists():
                    dst = backup_path / src.name
                    shutil.copy2(src, dst)
                    
            # Сохраняем информацию о бэкапе
            backup_info = {
                "timestamp": datetime.now().isoformat(),
                "files": list(changes.keys()),
                "changes": changes
            }
            
            with open(backup_path / "backup_info.json", "w") as f:
                json.dump(backup_info, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания бэкапа: {e}")
            return False
            
    async def restore_backup(self, backup_path: Path) -> bool:
        """Восстановление из резервной копии"""
        try:
            # Загружаем информацию о бэкапе
            with open(backup_path / "backup_info.json", "r") as f:
                backup_info = json.load(f)
                
            # Восстанавливаем файлы
            for file_path in backup_info["files"]:
                src = backup_path / Path(file_path).name
                if src.exists():
                    shutil.copy2(src, file_path)
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка восстановления бэкапа: {e}")
            return False
            
    def get_security_history(self) -> List[Dict[str, Any]]:
        """Получение истории проверок безопасности"""
        return self.security_history 