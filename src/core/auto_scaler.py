import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import psutil
import GPUtil
from pathlib import Path
import json
import yaml

class AutoScaler:
    """Система автоматического масштабирования"""
    
    def __init__(
        self,
        config_path: str = "config/system_config.yaml",
        min_nodes: int = 2,
        max_nodes: int = 10,
        scale_up_threshold: float = 0.8,
        scale_down_threshold: float = 0.3
    ):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
        
        # Параметры масштабирования
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        
        # Состояние системы
        self.node_metrics: Dict[str, List[float]] = {}
        self.scaling_history: List[Dict] = []
        
        # Создаем директорию для метрик
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> dict:
        """Загрузка конфигурации"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def get_system_metrics(self) -> Dict[str, float]:
        """Получение метрик системы"""
        metrics = {
            "cpu_usage": psutil.cpu_percent() / 100,
            "memory_usage": psutil.virtual_memory().percent / 100,
            "disk_usage": psutil.disk_usage('/').percent / 100
        }
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                metrics["gpu_usage"] = gpus[0].load
                metrics["gpu_memory"] = gpus[0].memoryUtil
        except Exception as e:
            self.logger.warning(f"Не удалось получить метрики GPU: {e}")
        
        return metrics
    
    async def get_node_metrics(self, node_id: str) -> Dict[str, float]:
        """Получение метрик узла"""
        if node_id not in self.node_metrics:
            self.node_metrics[node_id] = []
        
        metrics = await self.get_system_metrics()
        self.node_metrics[node_id].append(
            sum(metrics.values()) / len(metrics)
        )
        
        # Ограничиваем историю
        if len(self.node_metrics[node_id]) > 100:
            self.node_metrics[node_id] = self.node_metrics[node_id][-100:]
        
        return metrics
    
    async def should_scale_up(self) -> bool:
        """Проверка необходимости масштабирования вверх"""
        current_nodes = len(self.node_metrics)
        if current_nodes >= self.max_nodes:
            return False
        
        # Проверяем среднюю нагрузку всех узлов
        total_load = 0
        for metrics in self.node_metrics.values():
            if metrics:
                total_load += metrics[-1]
        
        avg_load = total_load / current_nodes if current_nodes > 0 else 0
        return avg_load > self.scale_up_threshold
    
    async def should_scale_down(self) -> bool:
        """Проверка необходимости масштабирования вниз"""
        current_nodes = len(self.node_metrics)
        if current_nodes <= self.min_nodes:
            return False
        
        # Проверяем среднюю нагрузку всех узлов
        total_load = 0
        for metrics in self.node_metrics.values():
            if metrics:
                total_load += metrics[-1]
        
        avg_load = total_load / current_nodes if current_nodes > 0 else 0
        return avg_load < self.scale_down_threshold
    
    async def scale_up(self) -> bool:
        """Масштабирование вверх"""
        current_nodes = len(self.node_metrics)
        if current_nodes >= self.max_nodes:
            return False
        
        try:
            # Создаем новый узел
            new_node_id = f"node{current_nodes + 1}"
            self.node_metrics[new_node_id] = []
            
            # Записываем историю масштабирования
            self.scaling_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "scale_up",
                "node_id": new_node_id,
                "reason": "high_load"
            })
            
            self.logger.info(f"Система масштабирована вверх: добавлен узел {new_node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка масштабирования вверх: {e}")
            return False
    
    async def scale_down(self) -> bool:
        """Масштабирование вниз"""
        current_nodes = len(self.node_metrics)
        if current_nodes <= self.min_nodes:
            return False
        
        try:
            # Находим наименее загруженный узел
            min_load_node = min(
                self.node_metrics.items(),
                key=lambda x: x[1][-1] if x[1] else float('inf')
            )[0]
            
            # Удаляем узел
            del self.node_metrics[min_load_node]
            
            # Записываем историю масштабирования
            self.scaling_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "scale_down",
                "node_id": min_load_node,
                "reason": "low_load"
            })
            
            self.logger.info(f"Система масштабирована вниз: удален узел {min_load_node}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка масштабирования вниз: {e}")
            return False
    
    async def save_metrics(self):
        """Сохранение метрик"""
        metrics_file = self.metrics_dir / "scaling_metrics.json"
        data = {
            "node_metrics": self.node_metrics,
            "scaling_history": self.scaling_history
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def start_monitoring(self, check_interval: int = 60):
        """Запуск мониторинга и масштабирования"""
        while True:
            try:
                # Обновляем метрики всех узлов
                for node_id in list(self.node_metrics.keys()):
                    await self.get_node_metrics(node_id)
                
                # Проверяем необходимость масштабирования
                if await self.should_scale_up():
                    await self.scale_up()
                elif await self.should_scale_down():
                    await self.scale_down()
                
                # Сохраняем метрики
                await self.save_metrics()
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Ошибка в мониторинге: {e}")
                await asyncio.sleep(60) 