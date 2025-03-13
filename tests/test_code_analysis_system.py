import pytest
import asyncio
from pathlib import Path
from src.core.code_analysis_system import CodeAnalysisSystem

@pytest.fixture
async def code_analysis_system(test_root, test_logger, test_config):
    """Создание экземпляра CodeAnalysisSystem для тестов"""
    system = CodeAnalysisSystem(
        system_root=test_root,
        logger=test_logger,
        config=test_config
    )
    await system.initialize()
    return system

@pytest.mark.asyncio
async def test_initialization(code_analysis_system):
    """Тест инициализации системы"""
    assert code_analysis_system.analysis_history is not None
    assert code_analysis_system.code_cache is not None

@pytest.mark.asyncio
async def test_analyze_code(code_analysis_system):
    """Тест анализа кода"""
    # Создаем тестовый файл
    test_file = code_analysis_system.system_root / "test.py"
    test_code = """
def complex_function(a, b, c):
    if a > b:
        if c > 0:
            return a + b + c
    return 0

class TestClass:
    def __init__(self, x):
        self.x = x
    
    def method(self, y):
        return self.x + y
    """
    test_file.write_text(test_code)
    
    # Анализируем код
    analysis_result = await code_analysis_system.analyze_code(test_file)
    
    assert analysis_result["file_path"] == str(test_file)
    assert analysis_result["complexity"] > 0
    assert len(analysis_result["patterns"]) > 0
    assert len(analysis_result["dependencies"]) >= 0
    assert len(analysis_result["improvements"]) > 0

@pytest.mark.asyncio
async def test_calculate_complexity(code_analysis_system):
    """Тест расчета сложности кода"""
    # Простой код
    simple_code = """
def simple_function(a, b):
    return a + b
    """
    complexity = code_analysis_system._calculate_complexity(simple_code)
    assert complexity == 1  # Минимальная сложность
    
    # Сложный код
    complex_code = """
def complex_function(a, b, c, d):
    if a > b:
        if c > d:
            if a + b > c + d:
                return True
    return False
    """
    complexity = code_analysis_system._calculate_complexity(complex_code)
    assert complexity > 3  # Высокая сложность

@pytest.mark.asyncio
async def test_analyze_patterns(code_analysis_system):
    """Тест анализа паттернов"""
    # Код с различными паттернами
    test_code = """
from abc import ABC, abstractmethod

class BaseClass(ABC):
    @abstractmethod
    def method(self):
        pass

class ConcreteClass(BaseClass):
    def method(self):
        return "implementation"

def factory_function():
    return ConcreteClass()
    """
    
    patterns = code_analysis_system._analyze_patterns(test_code)
    
    assert "inheritance" in patterns
    assert "abstract_class" in patterns
    assert "factory" in patterns

@pytest.mark.asyncio
async def test_analyze_dependencies(code_analysis_system):
    """Тест анализа зависимостей"""
    # Код с различными импортами
    test_code = """
import os
import sys
from pathlib import Path
from typing import List, Dict
import numpy as np
from .local_module import local_function
    """
    
    dependencies = code_analysis_system._analyze_dependencies(test_code)
    
    assert "os" in dependencies
    assert "sys" in dependencies
    assert "pathlib" in dependencies
    assert "typing" in dependencies
    assert "numpy" in dependencies
    assert "local_module" in dependencies

@pytest.mark.asyncio
async def test_find_improvements(code_analysis_system):
    """Тест поиска улучшений"""
    # Код с возможными улучшениями
    test_code = """
def long_function(a, b, c, d, e, f, g, h, i, j):
    result = 0
    if a > b:
        result += a
    if c > d:
        result += c
    if e > f:
        result += e
    if g > h:
        result += g
    if i > j:
        result += i
    return result
    """
    
    improvements = code_analysis_system._find_improvements(test_code)
    
    assert len(improvements) > 0
    assert any("function_length" in imp["type"] for imp in improvements)
    assert any("parameter_count" in imp["type"] for imp in improvements)

@pytest.mark.asyncio
async def test_search_code(code_analysis_system):
    """Тест поиска кода"""
    # Создаем тестовые файлы
    test_files = {
        "test1.py": "def search_function(): return True",
        "test2.py": "def another_search_function(): return False",
        "test3.py": "class SearchClass: pass"
    }
    
    for file_name, content in test_files.items():
        file_path = code_analysis_system.system_root / file_name
        file_path.write_text(content)
    
    # Ищем код
    search_results = await code_analysis_system.search_code("search")
    
    assert len(search_results) > 0
    assert any("search_function" in result["content"] for result in search_results)
    assert any("SearchClass" in result["content"] for result in search_results)

@pytest.mark.asyncio
async def test_analysis_history(code_analysis_system):
    """Тест истории анализа"""
    # Создаем и анализируем тестовый файл
    test_file = code_analysis_system.system_root / "test.py"
    test_file.write_text("def test_function(): pass")
    
    await code_analysis_system.analyze_code(test_file)
    
    history = code_analysis_system.get_analysis_history()
    assert len(history) > 0
    assert history[0]["file_path"] == str(test_file)
    assert "timestamp" in history[0]
    assert "complexity" in history[0]
    assert "patterns" in history[0]

@pytest.mark.asyncio
async def test_code_cache(code_analysis_system):
    """Тест кэширования кода"""
    # Создаем тестовый файл
    test_file = code_analysis_system.system_root / "test.py"
    test_code = "def cached_function(): return True"
    test_file.write_text(test_code)
    
    # Первый анализ
    result1 = await code_analysis_system.analyze_code(test_file)
    
    # Изменяем файл
    test_file.write_text("def cached_function(): return False")
    
    # Второй анализ (должен использовать кэш)
    result2 = await code_analysis_system.analyze_code(test_file)
    
    assert result1["complexity"] == result2["complexity"]  # Должен быть тот же результат из кэша 