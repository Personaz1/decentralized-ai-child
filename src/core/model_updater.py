import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
import aiohttp
from huggingface_hub import HfApi
from pathlib import Path
import yaml

class ModelUpdater:
    """Система автоматического обновления моделей"""
    
    def __init__(self, config_path: str = "config/model_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
        self.hf_api = HfApi()
        self.update_history: Dict[str, datetime] = {}
    
    def _load_config(self) -> dict:
        """Загрузка конфигурации"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def check_updates(self) -> Dict[str, bool]:
        """Проверка наличия обновлений для моделей"""
        updates = {}
        
        for model_type, model_config in self.config.items():
            try:
                # Получаем информацию о модели
                model_info = await self.hf_api.model_info(model_config['name'])
                
                # Проверяем последнее обновление
                last_update = self.update_history.get(model_type)
                if not last_update or model_info.last_modified > last_update:
                    updates[model_type] = True
                else:
                    updates[model_type] = False
                    
            except Exception as e:
                self.logger.error(f"Ошибка проверки обновлений для {model_type}: {e}")
                updates[model_type] = False
        
        return updates
    
    async def update_model(self, model_type: str) -> bool:
        """Обновление модели"""
        if model_type not in self.config:
            self.logger.error(f"Неизвестный тип модели: {model_type}")
            return False
        
        try:
            model_config = self.config[model_type]
            model_name = model_config['name']
            
            self.logger.info(f"Начало обновления модели {model_name}")
            
            # Скачиваем новую версию
            model_path = Path(f"models/{model_type}")
            model_path.mkdir(parents=True, exist_ok=True)
            
            await self.hf_api.download_folder(
                repo_id=model_name,
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            
            # Обновляем конфигурацию
            model_config['version'] = datetime.now().strftime("%Y%m%d")
            self.update_history[model_type] = datetime.now()
            
            # Сохраняем обновленную конфигурацию
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f)
            
            self.logger.info(f"Модель {model_name} успешно обновлена")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления модели {model_type}: {e}")
            return False
    
    async def start_update_monitor(self, check_interval: int = 3600):
        """Запуск мониторинга обновлений"""
        while True:
            try:
                updates = await self.check_updates()
                
                for model_type, needs_update in updates.items():
                    if needs_update:
                        self.logger.info(f"Обнаружено обновление для модели {model_type}")
                        success = await self.update_model(model_type)
                        
                        if success:
                            self.logger.info(f"Модель {model_type} успешно обновлена")
                        else:
                            self.logger.error(f"Не удалось обновить модель {model_type}")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Ошибка в мониторинге обновлений: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой 