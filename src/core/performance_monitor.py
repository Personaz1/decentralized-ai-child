from typing import Dict, List, Optional, Any
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
from collections import deque

@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    model_type: str
    timestamp: str
    inference_time: float
    memory_usage: float
    gpu_usage: float
    cpu_usage: float
    batch_size: int
    throughput: float
    error_rate: float
    quality_score: float

class PerformanceMonitor:
    """Мониторинг производительности системы"""
    
    def __init__(
        self,
        save_dir: str = "metrics",
        history_size: int = 1000,
        alert_thresholds: Optional[Dict[str, float]] = None
    ):
        self.metrics: Dict[str, deque] = {}
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.history_size = history_size
        self.alert_thresholds = alert_thresholds or {
            "inference_time": 1.0,  # секунды
            "memory_usage": 0.9,    # 90% от доступной памяти
            "gpu_usage": 0.9,       # 90% от доступной GPU
            "error_rate": 0.1,      # 10% ошибок
            "quality_score": 0.5    # минимальный балл качества
        }
        
        # Загружаем историю метрик
        self._load_metrics_history()
    
    def _load_metrics_history(self):
        """Загрузка истории метрик"""
        metrics_file = self.save_dir / "performance_metrics.json"
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                data = json.load(f)
                for model_type, metrics_list in data.items():
                    self.metrics[model_type] = deque(
                        [PerformanceMetrics(**m) for m in metrics_list],
                        maxlen=self.history_size
                    )
    
    def _save_metrics_history(self):
        """Сохранение истории метрик"""
        metrics_file = self.save_dir / "performance_metrics.json"
        data = {
            model_type: [
                {
                    "model_type": m.model_type,
                    "timestamp": m.timestamp,
                    "inference_time": m.inference_time,
                    "memory_usage": m.memory_usage,
                    "gpu_usage": m.gpu_usage,
                    "cpu_usage": m.cpu_usage,
                    "batch_size": m.batch_size,
                    "throughput": m.throughput,
                    "error_rate": m.error_rate,
                    "quality_score": m.quality_score
                }
                for m in metrics_list
            ]
            for model_type, metrics_list in self.metrics.items()
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def track_performance(
        self,
        model_type: str,
        metrics: Dict[str, float]
    ) -> None:
        """Отслеживание производительности"""
        # Создаем объект метрик
        performance_metrics = PerformanceMetrics(
            model_type=model_type,
            timestamp=datetime.now().isoformat(),
            **metrics
        )
        
        # Добавляем в историю
        if model_type not in self.metrics:
            self.metrics[model_type] = deque(maxlen=self.history_size)
        self.metrics[model_type].append(performance_metrics)
        
        # Сохраняем историю
        self._save_metrics_history()
        
        # Анализируем производительность
        await self._analyze_performance(model_type)
    
    async def _analyze_performance(self, model_type: str) -> None:
        """Анализ производительности"""
        if model_type not in self.metrics:
            return
        
        metrics_list = list(self.metrics[model_type])
        if not metrics_list:
            return
        
        latest_metrics = metrics_list[-1]
        
        # Проверяем пороговые значения
        alerts = []
        
        if latest_metrics.inference_time > self.alert_thresholds["inference_time"]:
            alerts.append(f"Высокое время инференса: {latest_metrics.inference_time:.2f}с")
        
        if latest_metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append(f"Высокое использование памяти: {latest_metrics.memory_usage:.2%}")
        
        if latest_metrics.gpu_usage > self.alert_thresholds["gpu_usage"]:
            alerts.append(f"Высокое использование GPU: {latest_metrics.gpu_usage:.2%}")
        
        if latest_metrics.error_rate > self.alert_thresholds["error_rate"]:
            alerts.append(f"Высокий процент ошибок: {latest_metrics.error_rate:.2%}")
        
        if latest_metrics.quality_score < self.alert_thresholds["quality_score"]:
            alerts.append(f"Низкое качество: {latest_metrics.quality_score:.2f}")
        
        # Отправляем уведомления
        if alerts:
            await self._send_alerts(model_type, alerts)
    
    async def _send_alerts(self, model_type: str, alerts: List[str]) -> None:
        """Отправка уведомлений"""
        alert_message = f"Внимание! Проблемы с производительностью модели {model_type}:\n"
        alert_message += "\n".join(f"- {alert}" for alert in alerts)
        
        self.logger.warning(alert_message)
        # TODO: Реализовать отправку уведомлений через webhook
    
    def get_performance_stats(
        self,
        model_type: str,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, float]:
        """Получение статистики производительности"""
        if model_type not in self.metrics:
            return {}
        
        metrics_list = list(self.metrics[model_type])
        if not metrics_list:
            return {}
        
        # Фильтруем по временному окну
        cutoff_time = datetime.now() - time_window
        recent_metrics = [
            m for m in metrics_list
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        # Вычисляем статистику
        stats = {
            "avg_inference_time": np.mean([m.inference_time for m in recent_metrics]),
            "avg_memory_usage": np.mean([m.memory_usage for m in recent_metrics]),
            "avg_gpu_usage": np.mean([m.gpu_usage for m in recent_metrics]),
            "avg_cpu_usage": np.mean([m.cpu_usage for m in recent_metrics]),
            "avg_throughput": np.mean([m.throughput for m in recent_metrics]),
            "avg_error_rate": np.mean([m.error_rate for m in recent_metrics]),
            "avg_quality_score": np.mean([m.quality_score for m in recent_metrics]),
            "max_inference_time": np.max([m.inference_time for m in recent_metrics]),
            "min_quality_score": np.min([m.quality_score for m in recent_metrics])
        }
        
        return stats
    
    def get_performance_trends(
        self,
        model_type: str,
        metric: str,
        time_window: timedelta = timedelta(hours=24)
    ) -> List[Dict[str, float]]:
        """Получение трендов производительности"""
        if model_type not in self.metrics:
            return []
        
        metrics_list = list(self.metrics[model_type])
        if not metrics_list:
            return []
        
        # Фильтруем по временному окну
        cutoff_time = datetime.now() - time_window
        recent_metrics = [
            m for m in metrics_list
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        if not recent_metrics:
            return []
        
        # Формируем тренд
        trend = [
            {
                "timestamp": m.timestamp,
                "value": getattr(m, metric)
            }
            for m in recent_metrics
        ]
        
        return trend
    
    async def cleanup_old_metrics(
        self,
        max_age_days: int = 30
    ) -> None:
        """Очистка старых метрик"""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        
        for model_type in list(self.metrics.keys()):
            self.metrics[model_type] = deque(
                [
                    m for m in self.metrics[model_type]
                    if datetime.fromisoformat(m.timestamp) > cutoff_time
                ],
                maxlen=self.history_size
            )
        
        self._save_metrics_history() 