from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import json
from datetime import datetime
import asyncio
import importlib.util
import sys

from .self_reflection import SelfReflectionSystem
from .self_evolution import SelfEvolutionSystem
from .auto_testing import AutoTestingSystem
from .validation_system import ValidationSystem
from .code_analysis_system import CodeAnalysisSystem
from .llm_system import LLMSystem
from .security_system import SecuritySystem

class DecentralizedAISystem:
    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.system_root = Path(__file__).parent.parent.parent
        
        # Инициализация компонентов
        self.reflection_system = SelfReflectionSystem(self.system_root)
        self.evolution_system = SelfEvolutionSystem(self.system_root)
        self.testing_system = AutoTestingSystem(self.system_root)
        self.validation_system = ValidationSystem(self.system_root)
        self.code_analysis_system = CodeAnalysisSystem(self.system_root)
        self.llm_system = LLMSystem(self.system_root)
        self.security_system = SecuritySystem(self.system_root)
        
        # Загрузка конфигурации
        self.config = self._load_config(config_path)
        
        # Инициализация метрик
        self.total_requests = 0
        self.average_response_time = 0
        self.nodes = {}
        
        # История изменений
        self.change_history = []
        
    async def start(self):
        """Запуск системы"""
        try:
            # Инициализируем LLM
            await self.llm_system.initialize()
            
            # Запускаем процессы самоанализа и эволюции
            asyncio.create_task(self._run_self_reflection())
            asyncio.create_task(self._run_evolution())
            asyncio.create_task(self._run_auto_testing())
            asyncio.create_task(self._run_code_analysis())
            
            self.logger.info("Система запущена")
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска системы: {e}")
            raise
            
    async def _run_self_reflection(self):
        """Запуск процесса самоанализа"""
        while True:
            try:
                # Анализируем кодовую базу
                analysis = await self.reflection_system.analyze_codebase()
                
                # Получаем предложения по улучшению
                improvements = await self.reflection_system.suggest_improvements(analysis)
                
                # Реализуем улучшения
                for improvement in improvements:
                    await self.reflection_system.implement_improvement(improvement)
                    
                # Ждем следующего цикла
                await asyncio.sleep(self.config["self_reflection"]["interval"])
                
            except Exception as e:
                self.logger.error(f"Ошибка самоанализа: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой
                
    async def _run_evolution(self):
        """Запуск процесса эволюции"""
        while True:
            try:
                # Запускаем эволюцию
                success = await self.evolution_system.evolve()
                
                if success:
                    self.logger.info("Эволюция успешно завершена")
                else:
                    self.logger.warning("Эволюция не удалась")
                    
                # Ждем следующего цикла
                await asyncio.sleep(self.config["evolution"]["interval"])
                
            except Exception as e:
                self.logger.error(f"Ошибка эволюции: {e}")
                await asyncio.sleep(60)
                
    async def _run_auto_testing(self):
        """Запуск автоматического тестирования"""
        while True:
            try:
                # Генерируем тесты
                tests = await self.testing_system.generate_tests()
                
                # Запускаем тесты
                results = await self.testing_system.run_tests(tests)
                
                # Анализируем результаты
                if results["failed"] > 0:
                    self.logger.warning(f"Найдено {results['failed']} упавших тестов")
                    
                # Ждем следующего цикла
                await asyncio.sleep(self.config["testing"]["interval"])
                
            except Exception as e:
                self.logger.error(f"Ошибка тестирования: {e}")
                await asyncio.sleep(60)
                
    async def _run_code_analysis(self):
        """Запуск анализа кода"""
        while True:
            try:
                # Анализируем код
                analysis = await self.code_analysis_system.analyze_code()
                
                # Ищем улучшения
                improvements = analysis["potential_improvements"]
                
                # Применяем улучшения
                for improvement in improvements:
                    await self._apply_improvement(improvement)
                    
                # Ждем следующего цикла
                await asyncio.sleep(self.config["code_analysis"]["interval"])
                
            except Exception as e:
                self.logger.error(f"Ошибка анализа кода: {e}")
                await asyncio.sleep(60)
                
    async def _apply_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Применение улучшения кода"""
        try:
            # Создаем бэкап перед изменениями
            if not await self.security_system.create_backup(improvement["changes"]):
                self.logger.error("Не удалось создать бэкап")
                return False
                
            # Проверяем безопасность изменений
            if not await self.security_system.validate_security(improvement["changes"]):
                self.logger.error("Изменения не прошли проверку безопасности")
                return False
                
            # Проверяем валидность изменений
            if not await self.validation_system.validate_changes(improvement["changes"]):
                self.logger.error("Изменения не прошли валидацию")
                return False
                
            # Применяем изменения
            for file_path, content in improvement["changes"].items():
                with open(file_path, "w") as f:
                    f.write(content)
                    
            # Перезагружаем модули
            for file_path in improvement["changes"]:
                await self._reload_module(file_path)
                
            # Сохраняем историю изменений
            self.change_history.append({
                "timestamp": datetime.now().isoformat(),
                "improvement": improvement,
                "status": "success"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка применения улучшения: {e}")
            
            # Восстанавливаем бэкап в случае ошибки
            backup_path = self.security_system.backup_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
            if backup_path.exists():
                await self.security_system.restore_backup(backup_path)
                
            self.change_history.append({
                "timestamp": datetime.now().isoformat(),
                "improvement": improvement,
                "status": "error",
                "error": str(e)
            })
            
            return False
            
    async def _generate_improved_code(self, current_code: str, 
                                    improvement: Dict[str, Any]) -> str:
        """Генерация улучшенного кода"""
        try:
            # Формируем контекст для LLM
            context = {
                "improvement_type": improvement["type"],
                "file": improvement["file"],
                "line": improvement["line"],
                "description": improvement["description"],
                "suggestion": improvement["suggestion"]
            }
            
            # Генерируем улучшенный код
            improved_code = await self.llm_system.improve_code(
                current_code,
                improvement["type"],
                context
            )
            
            return improved_code
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации улучшенного кода: {e}")
            return current_code
        
    async def _reload_module(self, file_path: str):
        """Перезагрузка модуля"""
        try:
            module_name = Path(file_path).stem
            if module_name in sys.modules:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
        except Exception as e:
            self.logger.error(f"Ошибка перезагрузки модуля {file_path}: {e}")
            
    async def search_and_improve(self, query: str) -> List[Dict[str, Any]]:
        """Поиск и улучшение кода"""
        results = []
        
        # Ищем код
        search_results = await self.code_analysis_system.search_code(query)
        
        # Анализируем результаты
        for result in search_results:
            if result["type"] == "local":
                # Анализируем код
                analysis = await self.code_analysis_system.analyze_code()
                
                # Ищем улучшения
                improvements = analysis["potential_improvements"]
                
                # Применяем улучшения
                for improvement in improvements:
                    if await self._apply_improvement(improvement):
                        results.append({
                            "file": improvement["file"],
                            "improvement": improvement,
                            "status": "success"
                        })
                        
        return results
        
    def _load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        if config_path is None:
            config_path = self.system_root / "config" / "system_config.yaml"
            
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Обработка сообщения"""
        try:
            # Получаем доступный узел
            node = await self.get_available_node()
            
            # Обрабатываем сообщение
            response = await node.process_message(message, context)
            
            # Обновляем метрики
            self.total_requests += 1
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + 
                 response["processing_time"]) / self.total_requests
            )
            
            return response["text"]
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки сообщения: {e}")
            raise
            
    async def get_available_node(self) -> Any:
        """Получение доступного узла"""
        available_nodes = []
        
        # Проверяем все узлы
        for node_id, node in self.nodes.items():
            # Получаем метрики узла
            metrics = await node.get_performance_metrics()
            
            # Проверяем доступность ресурсов
            if (metrics["cpu_usage"] < 0.8 and 
                metrics["memory_usage"] < 0.8 and 
                metrics["gpu_usage"] < 0.8):
                available_nodes.append((node, metrics))
                
        if not available_nodes:
            raise Exception("Нет доступных узлов для обработки запроса")
            
        # Сортируем узлы по приоритету
        available_nodes.sort(key=lambda x: (
            x[1]["cpu_usage"] + 
            x[1]["memory_usage"] + 
            x[1]["gpu_usage"]
        ))
        
        # Выбираем узел с наименьшей нагрузкой
        return available_nodes[0][0]
        
    def get_system_health(self) -> str:
        """Получение состояния системы"""
        if self.total_requests == 0:
            return "Нет данных"
            
        # Проверяем среднее время ответа
        if self.average_response_time > 1000:  # более 1 секунды
            return "Высокая нагрузка"
            
        # Проверяем количество активных узлов
        if len(self.nodes) < self.config["system"]["min_nodes"]:
            return "Недостаточно узлов"
            
        return "Нормальное"
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Получение метрик системы"""
        return {
            "total_requests": self.total_requests,
            "average_response_time": self.average_response_time,
            "active_nodes": len(self.nodes),
            "system_health": self.get_system_health(),
            "reflection_history": self.reflection_system.get_reflection_history(),
            "evolution_history": self.evolution_system.get_evolution_history(),
            "test_history": self.testing_system.get_test_history(),
            "validation_history": self.validation_system.get_validation_history(),
            "analysis_history": self.code_analysis_system.get_analysis_history()
        }
        
    def get_change_history(self) -> List[Dict[str, Any]]:
        """Получение истории изменений"""
        return self.change_history
        
    def get_security_history(self) -> List[Dict[str, Any]]:
        """Получение истории проверок безопасности"""
        return self.security_system.get_security_history()
        
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """Получение истории валидации"""
        return self.validation_system.get_validation_history()
        
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Получение истории анализа кода"""
        return self.code_analysis_system.get_analysis_history() 