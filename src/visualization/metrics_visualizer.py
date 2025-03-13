import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
import time
import numpy as np
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class MetricsVisualizer:
    """Визуализация метрик системы"""
    
    def __init__(self, metrics_path: str = "metrics/system_metrics.json"):
        self.metrics_path = metrics_path
        self.fig = None
        self.notification_webhook = os.getenv("NOTIFICATION_WEBHOOK")
        self.last_notification_time = {}
        self.notification_cooldown = 300  # 5 минут между уведомлениями
    
    def load_metrics(self) -> pd.DataFrame:
        """Загрузка метрик из файла"""
        with open(self.metrics_path, 'r') as f:
            metrics = json.load(f)
        
        # Преобразуем в DataFrame
        data = []
        for round_metrics in metrics:
            round_data = {
                'round': round_metrics['round'],
                'timestamp': round_metrics['timestamp']
            }
            for node_id, node_metrics in round_metrics['nodes'].items():
                for metric_name, value in node_metrics.items():
                    round_data[f'{node_id}_{metric_name}'] = value
            data.append(round_data)
        
        return pd.DataFrame(data)
    
    def send_notification(self, title: str, message: str, level: str = "info"):
        """Отправка уведомления"""
        if not self.notification_webhook:
            return
        
        current_time = time.time()
        notification_key = f"{title}_{level}"
        
        # Проверяем cooldown
        if notification_key in self.last_notification_time:
            if current_time - self.last_notification_time[notification_key] < self.notification_cooldown:
                return
        
        try:
            payload = {
                "title": title,
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(self.notification_webhook, json=payload)
            if response.status_code == 200:
                self.last_notification_time[notification_key] = current_time
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")
    
    def create_dashboard(self):
        """Создание интерактивной панели мониторинга"""
        df = self.load_metrics()
        
        # Создаем подграфики
        self.fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Качество ответов по узлам',
                'Скорость обучения',
                'Успешность валидации',
                '3D визуализация метрик'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "scatter3d"}]
            ]
        )
        
        # График качества ответов
        for node_id in df.columns:
            if 'response_quality' in node_id:
                self.fig.add_trace(
                    go.Scatter(
                        x=df['round'],
                        y=df[node_id],
                        name=node_id.split('_')[0],
                        mode='lines+markers'
                    ),
                    row=1, col=1
                )
                
                # Проверяем качество ответов
                if df[node_id].iloc[-1] < 0.5:
                    self.send_notification(
                        "Низкое качество ответов",
                        f"Узел {node_id.split('_')[0]} показывает низкое качество ответов: {df[node_id].iloc[-1]:.2f}",
                        "warning"
                    )
        
        # График скорости обучения
        for node_id in df.columns:
            if 'learning_rate' in node_id:
                self.fig.add_trace(
                    go.Scatter(
                        x=df['round'],
                        y=df[node_id],
                        name=node_id.split('_')[0],
                        mode='lines+markers'
                    ),
                    row=1, col=2
                )
                
                # Проверяем скорость обучения
                if df[node_id].iloc[-1] > 0.1:
                    self.send_notification(
                        "Высокая скорость обучения",
                        f"Узел {node_id.split('_')[0]} показывает высокую скорость обучения: {df[node_id].iloc[-1]:.2f}",
                        "warning"
                    )
        
        # График успешности валидации
        for node_id in df.columns:
            if 'validation_success' in node_id:
                self.fig.add_trace(
                    go.Scatter(
                        x=df['round'],
                        y=df[node_id],
                        name=node_id.split('_')[0],
                        mode='lines+markers'
                    ),
                    row=2, col=1
                )
        
        # 3D визуализация метрик
        for node_id in df.columns:
            if 'response_quality' in node_id:
                node_base = node_id.split('_')[0]
                
                # Создаем 3D график
                self.fig.add_trace(
                    go.Scatter3d(
                        x=df['round'],
                        y=df[f'{node_base}_response_quality'],
                        z=df[f'{node_base}_learning_rate'],
                        name=f'{node_base}_3d',
                        mode='markers',
                        marker=dict(
                            size=8,
                            color=df[f'{node_base}_validation_success'],
                            colorscale='Viridis',
                            opacity=0.8
                        )
                    ),
                    row=2, col=2
                )
        
        # Обновляем layout
        self.fig.update_layout(
            height=1000,
            width=1400,
            title_text="Панель мониторинга системы",
            showlegend=True,
            scene=dict(
                xaxis_title='Раунд',
                yaxis_title='Качество ответов',
                zaxis_title='Скорость обучения'
            )
        )
        
        # Сохраняем график
        self.fig.write_html("metrics/dashboard.html")
        
        # Проверяем общую производительность
        self._check_system_performance(df)
    
    def _check_system_performance(self, df: pd.DataFrame):
        """Проверка общей производительности системы"""
        # Собираем средние метрики по всем узлам
        avg_metrics = {
            'response_quality': 0.0,
            'learning_rate': 0.0,
            'validation_success': 0.0
        }
        
        node_count = 0
        for node_id in df.columns:
            if 'response_quality' in node_id:
                node_base = node_id.split('_')[0]
                avg_metrics['response_quality'] += df[f'{node_base}_response_quality'].iloc[-1]
                avg_metrics['learning_rate'] += df[f'{node_base}_learning_rate'].iloc[-1]
                avg_metrics['validation_success'] += df[f'{node_base}_validation_success'].iloc[-1]
                node_count += 1
        
        if node_count > 0:
            for metric in avg_metrics:
                avg_metrics[metric] /= node_count
        
        # Проверяем критические метрики
        if avg_metrics['response_quality'] < 0.6:
            self.send_notification(
                "Критическое качество системы",
                f"Среднее качество ответов системы критически низкое: {avg_metrics['response_quality']:.2f}",
                "error"
            )
        
        if avg_metrics['learning_rate'] > 0.15:
            self.send_notification(
                "Критическая скорость обучения",
                f"Средняя скорость обучения системы критически высокая: {avg_metrics['learning_rate']:.2f}",
                "error"
            )
    
    def update_dashboard(self):
        """Обновление панели мониторинга"""
        while True:
            self.create_dashboard()
            time.sleep(5)  # Обновляем каждые 5 секунд 