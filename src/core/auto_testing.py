from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import json
from datetime import datetime
import asyncio
import pytest
import coverage
import ast
import random

class AutoTestingSystem:
    def __init__(self, system_root: Path):
        self.system_root = system_root
        self.logger = logging.getLogger(__name__)
        self.test_history = []
        self.coverage_history = []
        
    async def generate_tests(self) -> List[Dict[str, Any]]:
        """Генерация тестов на основе анализа кода"""
        tests = []
        
        # Анализируем все Python файлы
        for file_path in self.system_root.rglob("*.py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Анализируем код
                tree = ast.parse(content)
                
                # Генерируем тесты для функций
                function_tests = self._generate_function_tests(tree)
                
                # Генерируем тесты для классов
                class_tests = self._generate_class_tests(tree)
                
                tests.extend(function_tests)
                tests.extend(class_tests)
                
            except Exception as e:
                self.logger.error(f"Ошибка генерации тестов для {file_path}: {e}")
                
        return tests
    
    def _generate_function_tests(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Генерация тестов для функций"""
        tests = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Генерируем тестовые данные
                test_data = self._generate_test_data(node)
                
                # Создаем тест
                test = {
                    "name": f"test_{node.name}",
                    "type": "function",
                    "target": node.name,
                    "data": test_data,
                    "expected": self._generate_expected_result(node)
                }
                
                tests.append(test)
                
        return tests
    
    def _generate_class_tests(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Генерация тестов для классов"""
        tests = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Генерируем тесты для методов
                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        test_data = self._generate_test_data(method)
                        
                        test = {
                            "name": f"test_{node.name}_{method.name}",
                            "type": "method",
                            "target": f"{node.name}.{method.name}",
                            "data": test_data,
                            "expected": self._generate_expected_result(method)
                        }
                        
                        tests.append(test)
                        
        return tests
    
    def _generate_test_data(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Генерация тестовых данных"""
        test_data = {}
        
        # Анализируем параметры функции
        for arg in node.args.args:
            # Генерируем случайные значения в зависимости от типа
            if arg.annotation:
                test_data[arg.arg] = self._generate_value_by_type(arg.annotation)
            else:
                test_data[arg.arg] = self._generate_random_value()
                
        return test_data
    
    def _generate_value_by_type(self, type_node: ast.AST) -> Any:
        """Генерация значения по типу"""
        if isinstance(type_node, ast.Name):
            if type_node.id == "int":
                return random.randint(-100, 100)
            elif type_node.id == "float":
                return random.uniform(-100, 100)
            elif type_node.id == "str":
                return f"test_{random.randint(1, 1000)}"
            elif type_node.id == "bool":
                return random.choice([True, False])
            elif type_node.id == "list":
                return []
            elif type_node.id == "dict":
                return {}
                
        return None
    
    def _generate_random_value(self) -> Any:
        """Генерация случайного значения"""
        types = [int, float, str, bool, list, dict]
        value_type = random.choice(types)
        
        if value_type == int:
            return random.randint(-100, 100)
        elif value_type == float:
            return random.uniform(-100, 100)
        elif value_type == str:
            return f"test_{random.randint(1, 1000)}"
        elif value_type == bool:
            return random.choice([True, False])
        elif value_type == list:
            return []
        elif value_type == dict:
            return {}
            
    def _generate_expected_result(self, node: ast.FunctionDef) -> Any:
        """Генерация ожидаемого результата"""
        # Анализируем возвращаемое значение
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                if child.value:
                    return self._generate_value_by_type(child.value)
                    
        return None
    
    async def run_tests(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Запуск тестов"""
        results = {
            "total": len(tests),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "details": []
        }
        
        # Запускаем тесты с измерением покрытия
        cov = coverage.Coverage()
        cov.start()
        
        for test in tests:
            try:
                # Создаем тестовый файл
                test_file = self._create_test_file(test)
                
                # Запускаем тест
                result = pytest.main(["-v", str(test_file)])
                
                # Анализируем результат
                if result == 0:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    
                results["details"].append({
                    "name": test["name"],
                    "status": "passed" if result == 0 else "failed",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                results["errors"] += 1
                results["details"].append({
                    "name": test["name"],
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                
        # Останавливаем измерение покрытия
        cov.stop()
        cov.save()
        
        # Получаем отчет о покрытии
        coverage_data = self._get_coverage_report(cov)
        
        # Сохраняем результаты
        self.test_history.append({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "coverage": coverage_data
        })
        
        return results
    
    def _create_test_file(self, test: Dict[str, Any]) -> Path:
        """Создание файла с тестом"""
        test_dir = self.system_root / "tests"
        test_dir.mkdir(exist_ok=True)
        
        test_file = test_dir / f"{test['name']}.py"
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(self._generate_test_code(test))
            
        return test_file
    
    def _generate_test_code(self, test: Dict[str, Any]) -> str:
        """Генерация кода теста"""
        code = f"""
def {test['name']}():
    # Подготовка тестовых данных
    test_data = {test['data']}
    expected = {test['expected']}
    
    # Вызов тестируемой функции
    result = {test['target']}(**test_data)
    
    # Проверка результата
    assert result == expected
"""
        return code
    
    def _get_coverage_report(self, cov: coverage.Coverage) -> Dict[str, Any]:
        """Получение отчета о покрытии"""
        report = {
            "total_lines": 0,
            "covered_lines": 0,
            "missing_lines": 0,
            "coverage_percentage": 0
        }
        
        # Анализируем отчет
        for filename in cov.get_data().measured_files():
            analysis = cov.analysis2(filename)
            report["total_lines"] += analysis[1]
            report["covered_lines"] += analysis[1] - len(analysis[2])
            report["missing_lines"] += len(analysis[2])
            
        if report["total_lines"] > 0:
            report["coverage_percentage"] = (
                report["covered_lines"] / report["total_lines"] * 100
            )
            
        return report
    
    def get_test_history(self) -> List[Dict[str, Any]]:
        """Получение истории тестирования"""
        return self.test_history 