import asyncio
import logging
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import aiofiles
import yaml

class BackupSystem:
    """Система автоматического бэкапа и восстановления"""
    
    def __init__(
        self,
        backup_dir: str = "backups",
        max_backups: int = 5,
        backup_interval: int = 3600,
        retention_days: int = 7
    ):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.max_backups = max_backups
        self.backup_interval = backup_interval
        self.retention_days = retention_days
        self.logger = logging.getLogger(__name__)
        
        # Создаем файл для хранения метаданных бэкапов
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.backup_metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Загрузка метаданных бэкапов"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"backups": []}
    
    async def _save_metadata(self):
        """Сохранение метаданных бэкапов"""
        async with aiofiles.open(self.metadata_file, 'w') as f:
            await f.write(json.dumps(self.backup_metadata, indent=2))
    
    async def create_backup(self) -> bool:
        """Создание бэкапа системы"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            
            # Создаем директорию для бэкапа
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Копируем важные директории
            directories_to_backup = [
                "models",
                "knowledge",
                "metrics",
                "config"
            ]
            
            for directory in directories_to_backup:
                src = Path(directory)
                if src.exists():
                    dst = backup_path / directory
                    shutil.copytree(src, dst)
            
            # Сохраняем конфигурацию системы
            config_files = [
                "config/system_config.yaml",
                "config/model_config.yaml"
            ]
            
            for config_file in config_files:
                src = Path(config_file)
                if src.exists():
                    dst = backup_path / "config" / src.name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
            
            # Обновляем метаданные
            self.backup_metadata["backups"].append({
                "timestamp": timestamp,
                "path": str(backup_path),
                "size": self._get_backup_size(backup_path),
                "status": "completed"
            })
            
            # Ограничиваем количество бэкапов
            if len(self.backup_metadata["backups"]) > self.max_backups:
                oldest_backup = self.backup_metadata["backups"].pop(0)
                self._remove_backup(oldest_backup["path"])
            
            await self._save_metadata()
            self.logger.info(f"Бэкап успешно создан: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания бэкапа: {e}")
            return False
    
    def _get_backup_size(self, backup_path: Path) -> int:
        """Получение размера бэкапа в байтах"""
        total_size = 0
        for path in backup_path.rglob("*"):
            if path.is_file():
                total_size += path.stat().st_size
        return total_size
    
    def _remove_backup(self, backup_path: str):
        """Удаление бэкапа"""
        try:
            shutil.rmtree(backup_path)
            self.logger.info(f"Бэкап удален: {backup_path}")
        except Exception as e:
            self.logger.error(f"Ошибка удаления бэкапа: {e}")
    
    async def restore_backup(self, timestamp: str) -> bool:
        """Восстановление системы из бэкапа"""
        try:
            # Находим бэкап по временной метке
            backup = next(
                (b for b in self.backup_metadata["backups"] if b["timestamp"] == timestamp),
                None
            )
            
            if not backup:
                self.logger.error(f"Бэкап не найден: {timestamp}")
                return False
            
            backup_path = Path(backup["path"])
            
            # Восстанавливаем директории
            for item in backup_path.iterdir():
                if item.is_dir():
                    dst = Path(item.name)
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(item, dst)
            
            # Восстанавливаем конфигурационные файлы
            config_backup = backup_path / "config"
            if config_backup.exists():
                for config_file in config_backup.glob("*.yaml"):
                    dst = Path("config") / config_file.name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(config_file, dst)
            
            self.logger.info(f"Система успешно восстановлена из бэкапа: {timestamp}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка восстановления из бэкапа: {e}")
            return False
    
    async def cleanup_old_backups(self):
        """Очистка старых бэкапов"""
        current_time = datetime.now()
        backups_to_remove = []
        
        for backup in self.backup_metadata["backups"]:
            backup_time = datetime.strptime(backup["timestamp"], "%Y%m%d_%H%M%S")
            age_days = (current_time - backup_time).days
            
            if age_days > self.retention_days:
                backups_to_remove.append(backup)
        
        for backup in backups_to_remove:
            self.backup_metadata["backups"].remove(backup)
            self._remove_backup(backup["path"])
        
        if backups_to_remove:
            await self._save_metadata()
            self.logger.info(f"Удалено {len(backups_to_remove)} старых бэкапов")
    
    async def start_backup_monitor(self):
        """Запуск мониторинга и создания бэкапов"""
        while True:
            try:
                await self.create_backup()
                await self.cleanup_old_backups()
                await asyncio.sleep(self.backup_interval)
            except Exception as e:
                self.logger.error(f"Ошибка в мониторинге бэкапов: {e}")
                await asyncio.sleep(60) 