import unittest
import asyncio
import json
from pathlib import Path
from src.core.gemma_node import GemmaNode
from src.core.consensus import Consensus
from src.visualization.metrics_visualizer import MetricsVisualizer

class TestDecentralizedAISystem(unittest.TestCase):
    """Тесты для децентрализованной AI системы"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)
        
        # Создаем тестовые узлы
        self.node1 = GemmaNode(
            node_id="test_node_1",
            position=(0, 0),
            model_name="google/gemma-1b"
        )
        self.node2 = GemmaNode(
            node_id="test_node_2",
            position=(1, 1),
            model_name="google/gemma-1b"
        )
        
        # Создаем тестовый консенсус
        self.consensus = Consensus()
        self.consensus.add_validator(self.node1.node_id)
        self.consensus.add_validator(self.node2.node_id)
        
        # Создаем визуализатор
        self.visualizer = MetricsVisualizer(
            metrics_path=str(self.test_dir / "test_metrics.json")
        )
    
    def tearDown(self):
        """Очистка после тестов"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_node_creation(self):
        """Тест создания узлов"""
        self.assertIsNotNone(self.node1)
        self.assertIsNotNone(self.node2)
        self.assertEqual(self.node1.node_id, "test_node_1")
        self.assertEqual(self.node2.node_id, "test_node_2")
    
    def test_node_communication(self):
        """Тест коммуникации между узлами"""
        async def test_comm():
            # Отправляем сообщение от node1 к node2
            message = "Тестовое сообщение"
            response = await self.node1.communicate(self.node2, message)
            
            self.assertIsNotNone(response)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
        
        asyncio.run(test_comm())
    
    def test_consensus_validation(self):
        """Тест валидации консенсуса"""
        # Создаем тестовый блок
        changes = {"test": "data"}
        block = self.consensus.create_block(
            node_id=self.node1.node_id,
            changes=changes
        )
        
        # Проверяем создание блока
        self.assertIsNotNone(block)
        self.assertEqual(block.node_id, self.node1.node_id)
        self.assertEqual(block.changes, changes)
        
        # Валидируем блок
        self.consensus.validate_block(block.hash, self.node1.node_id)
        self.consensus.validate_block(block.hash, self.node2.node_id)
        
        # Проверяем статус блока
        self.assertEqual(block.status, "validated")
    
    def test_metrics_visualization(self):
        """Тест визуализации метрик"""
        # Создаем тестовые метрики
        test_metrics = {
            "round": 1,
            "timestamp": "2024-03-20T12:00:00",
            "nodes": {
                "test_node_1": {
                    "response_quality": 0.8,
                    "learning_rate": 0.05,
                    "validation_success": 1.0
                },
                "test_node_2": {
                    "response_quality": 0.7,
                    "learning_rate": 0.06,
                    "validation_success": 0.9
                }
            }
        }
        
        # Сохраняем метрики
        metrics_file = self.test_dir / "test_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump([test_metrics], f)
        
        # Создаем дашборд
        self.visualizer.create_dashboard()
        
        # Проверяем создание файла дашборда
        dashboard_file = Path("metrics/dashboard.html")
        self.assertTrue(dashboard_file.exists())
    
    def test_node_learning(self):
        """Тест обучения узлов"""
        async def test_learning():
            # Создаем опыт для обучения
            experience = {
                "input": "Тестовый ввод",
                "output": "Тестовый вывод",
                "quality": 0.9
            }
            
            # Обучаем узел
            await self.node1.learn_from_experience(experience)
            
            # Проверяем, что опыт был добавлен
            self.assertTrue(len(self.node1.state.experience) > 0)
            self.assertEqual(self.node1.state.experience[-1], experience)
        
        asyncio.run(test_learning())
    
    def test_system_performance(self):
        """Тест производительности системы"""
        # Создаем тестовые метрики с низкой производительностью
        test_metrics = {
            "round": 1,
            "timestamp": "2024-03-20T12:00:00",
            "nodes": {
                "test_node_1": {
                    "response_quality": 0.4,  # Критически низкое качество
                    "learning_rate": 0.2,    # Критически высокая скорость
                    "validation_success": 0.5
                }
            }
        }
        
        # Сохраняем метрики
        metrics_file = self.test_dir / "test_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump([test_metrics], f)
        
        # Проверяем отправку уведомлений
        self.visualizer.create_dashboard()
        # В реальном тесте здесь нужно проверить отправку уведомлений
        # Это можно сделать через моки или перехват HTTP-запросов

if __name__ == '__main__':
    unittest.main() 