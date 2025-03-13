from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import ast
import re
from datetime import datetime
import aiohttp
import asyncio

class CodeAnalysisSystem:
    def __init__(self, system_root: Path):
        self.system_root = system_root
        self.logger = logging.getLogger(__name__)
        self.analysis_history = []
        self.code_cache = {}
        
    async def analyze_code(self) -> Dict[str, Any]:
        """Анализ кодовой базы"""
        analysis = {
            "complexity": {},
            "patterns": {},
            "dependencies": {},
            "potential_improvements": []
        }
        
        # Анализируем все Python файлы
        for file_path in self.system_root.rglob("*.py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Анализируем сложность
                tree = ast.parse(content)
                complexity = self._calculate_complexity(tree)
                
                # Анализируем паттерны
                patterns = self._analyze_patterns(tree)
                
                # Анализируем зависимости
                dependencies = self._analyze_dependencies(tree)
                
                analysis["complexity"][str(file_path)] = complexity
                analysis["patterns"][str(file_path)] = patterns
                analysis["dependencies"][str(file_path)] = dependencies
                
                # Ищем потенциальные улучшения
                improvements = self._find_improvements(file_path, content)
                analysis["potential_improvements"].extend(improvements)
                
            except Exception as e:
                self.logger.error(f"Ошибка анализа файла {file_path}: {e}")
                
        # Сохраняем историю анализа
        self.analysis_history.append({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis
        })
        
        return analysis
        
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Расчет цикломатической сложности"""
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
                
        return complexity
        
    def _analyze_patterns(self, tree: ast.AST) -> List[str]:
        """Анализ паттернов проектирования"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Проверяем наследование
                if len(node.bases) > 0:
                    patterns.append("inheritance")
                    
                # Проверяем декораторы
                if any(d.id == "abstractmethod" for d in node.decorator_list):
                    patterns.append("abstract_class")
                    
        return patterns
        
    def _analyze_dependencies(self, tree: ast.AST) -> List[str]:
        """Анализ зависимостей"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                dependencies.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                dependencies.append(node.module)
                
        return dependencies
        
    def _find_improvements(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Поиск потенциальных улучшений"""
        improvements = []
        
        # Проверяем длину функций
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 20:
                    improvements.append({
                        "type": "function_length",
                        "file": str(file_path),
                        "line": node.lineno,
                        "description": f"Функция {node.name} слишком длинная ({len(node.body)} строк)",
                        "suggestion": "Разбить на более мелкие функции"
                    })
                    
        # Проверяем сложность условий
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if len(node.body) > 10:
                    improvements.append({
                        "type": "condition_complexity",
                        "file": str(file_path),
                        "line": node.lineno,
                        "description": "Сложное условие",
                        "suggestion": "Упростить условие или разбить на части"
                    })
                    
        return improvements
        
    async def search_code(self, query: str) -> List[Dict[str, Any]]:
        """Поиск кода по запросу"""
        results = []
        
        # Поиск в локальной кодовой базе
        for file_path in self.system_root.rglob("*.py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                if query.lower() in content.lower():
                    results.append({
                        "file": str(file_path),
                        "content": content,
                        "type": "local"
                    })
                    
            except Exception as e:
                self.logger.error(f"Ошибка поиска в файле {file_path}: {e}")
                
        # Поиск в интернете
        try:
            async with aiohttp.ClientSession() as session:
                # Поиск на GitHub
                async with session.get(
                    f"https://api.github.com/search/code?q={query}",
                    headers={"Accept": "application/vnd.github.v3+json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data.get("items", []):
                            results.append({
                                "file": item["html_url"],
                                "content": item["description"],
                                "type": "github"
                            })
                            
        except Exception as e:
            self.logger.error(f"Ошибка поиска в интернете: {e}")
            
        return results
        
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Получение истории анализа"""
        return self.analysis_history 