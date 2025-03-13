import pytest
import asyncio
from pathlib import Path
from src.core.llm_system import LLMSystem

@pytest.fixture
async def llm_system(test_root, test_logger, test_config):
    """Создание экземпляра LLMSystem для тестов"""
    system = LLMSystem(
        system_root=test_root,
        logger=test_logger,
        config=test_config
    )
    await system.initialize()
    return system

@pytest.mark.asyncio
async def test_initialization(llm_system):
    """Тест инициализации системы"""
    assert llm_system.model is not None
    assert llm_system.tokenizer is not None
    assert llm_system.device in ["cuda", "cpu"]
    assert llm_system.cache is not None
    assert llm_system.generation_history is not None

@pytest.mark.asyncio
async def test_generate_code(llm_system):
    """Тест генерации кода"""
    prompt = "Создай функцию для сложения двух чисел"
    context = {"language": "python"}
    
    code = await llm_system.generate_code(prompt, context)
    
    assert code is not None
    assert isinstance(code, str)
    assert "def" in code
    assert "return" in code
    assert len(code) > 0

@pytest.mark.asyncio
async def test_improve_code(llm_system):
    """Тест улучшения кода"""
    original_code = """
def add(a, b):
    return a + b
    """
    
    improvement = {
        "type": "optimization",
        "description": "Добавить проверку типов и документацию"
    }
    
    improved_code = await llm_system.improve_code(original_code, improvement)
    
    assert improved_code is not None
    assert isinstance(improved_code, str)
    assert "def" in improved_code
    assert "return" in improved_code
    assert "type" in improved_code.lower()
    assert "docstring" in improved_code.lower() or '"""' in improved_code

@pytest.mark.asyncio
async def test_cache_mechanism(llm_system):
    """Тест механизма кэширования"""
    prompt = "Создай функцию для умножения двух чисел"
    context = {"language": "python"}
    
    # Первый вызов
    code1 = await llm_system.generate_code(prompt, context)
    
    # Второй вызов с теми же параметрами
    code2 = await llm_system.generate_code(prompt, context)
    
    assert code1 == code2
    assert llm_system.cache_hits > 0

@pytest.mark.asyncio
async def test_error_handling(llm_system):
    """Тест обработки ошибок"""
    # Тест с неверным промптом
    with pytest.raises(Exception):
        await llm_system.generate_code("", {})
    
    # Тест с неверным контекстом
    with pytest.raises(Exception):
        await llm_system.generate_code("test", None)
    
    # Тест с неверным кодом для улучшения
    with pytest.raises(Exception):
        await llm_system.improve_code("invalid code", {"type": "test"})

@pytest.mark.asyncio
async def test_generation_history(llm_system):
    """Тест истории генераций"""
    prompt = "Создай функцию для деления двух чисел"
    context = {"language": "python"}
    
    await llm_system.generate_code(prompt, context)
    
    history = llm_system.get_generation_history()
    assert len(history) > 0
    assert history[0]["prompt"] == prompt
    assert history[0]["context"] == context
    assert "timestamp" in history[0]
    assert "success" in history[0]

@pytest.mark.asyncio
async def test_complexity_validation(llm_system):
    """Тест валидации сложности кода"""
    # Создаем сложный код
    complex_code = """
def complex_function(a, b, c, d, e, f, g, h, i, j):
    if a > b:
        if c > d:
            if e > f:
                if g > h:
                    if i > j:
                        return True
    return False
    """
    
    # Проверяем, что система определяет высокую сложность
    complexity = llm_system._calculate_complexity(complex_code)
    assert complexity > 10  # Высокая сложность
    
    # Проверяем улучшение
    improvement = {
        "type": "complexity_reduction",
        "description": "Упростить логику функции"
    }
    
    improved_code = await llm_system.improve_code(complex_code, improvement)
    new_complexity = llm_system._calculate_complexity(improved_code)
    
    assert new_complexity < complexity  # Сложность должна уменьшиться 