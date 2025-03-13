from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import json
from datetime import datetime
import ast
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from huggingface_hub import hf_hub_download
import os
import hashlib
import pickle

class LLMSystem:
    def __init__(self, system_root: Path):
        self.system_root = system_root
        self.logger = logging.getLogger(__name__)
        self.generation_history = []
        self.model = None
        self.tokenizer = None
        self.model_name = "google/gemma-3-4b-it"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_dir = self.system_root / "models"
        self.cache_dir = self.system_root / "cache"
        self.model_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache = {}
        self.max_cache_size = 1000  # Максимальное количество кэшированных результатов
        self.model_dir.mkdir(exist_ok=True)
        
    async def initialize(self):
        """Инициализация LLM"""
        try:
            self.logger.info(f"Начинаем загрузку модели {self.model_name}")
            
            # Загружаем токенизатор
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.model_dir,
                trust_remote_code=True
            )
            self.logger.info("Токенизатор загружен")
            
            # Загружаем модель
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir=self.model_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto",
                trust_remote_code=True
            )
            self.logger.info("Модель загружена")
            
            # Настраиваем параметры генерации
            self.generation_config = {
                "max_length": 2048,
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True,
                "pad_token_id": self.tokenizer.pad_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
                "repetition_penalty": 1.1
            }
            
            self.logger.info("LLM успешно инициализирован")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации LLM: {e}")
            raise
            
    def _get_cache_key(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Создание ключа кэша"""
        cache_data = {
            "prompt": prompt,
            "context": context,
            "model": self.model_name,
            "config": self.generation_config
        }
        return hashlib.sha256(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
        
    def _load_cache(self):
        """Загрузка кэша из файла"""
        try:
            cache_file = self.cache_dir / "generation_cache.pkl"
            if cache_file.exists():
                with open(cache_file, "rb") as f:
                    self.cache = pickle.load(f)
                self.logger.info(f"Загружен кэш с {len(self.cache)} записями")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки кэша: {e}")
            
    def _save_cache(self):
        """Сохранение кэша в файл"""
        try:
            cache_file = self.cache_dir / "generation_cache.pkl"
            with open(cache_file, "wb") as f:
                pickle.dump(self.cache, f)
            self.logger.info(f"Сохранен кэш с {len(self.cache)} записями")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения кэша: {e}")
            
    async def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Генерация кода на основе промпта"""
        try:
            # Проверяем кэш
            cache_key = self._get_cache_key(prompt, context)
            if cache_key in self.cache:
                self.logger.info("Используем результат из кэша")
                return self.cache[cache_key]
            
            # Форматируем промпт
            formatted_prompt = self._format_prompt(prompt, context)
            
            # Токенизируем входной текст
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.generation_config["max_length"]
            ).to(self.device)
            
            # Генерируем код
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    **self.generation_config
                )
            
            # Декодируем результат
            generated_code = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            # Извлекаем только код из ответа
            code_match = re.search(r"```python\n(.*?)\n```", generated_code, re.DOTALL)
            if code_match:
                generated_code = code_match.group(1).strip()
            
            # Сохраняем в кэш
            if len(self.cache) >= self.max_cache_size:
                # Удаляем старые записи
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[cache_key] = generated_code
            self._save_cache()
            
            # Сохраняем историю
            self.generation_history.append({
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "context": context,
                "generated_code": generated_code,
                "status": "success",
                "cache_hit": False
            })
            
            return generated_code
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации кода: {e}")
            self.generation_history.append({
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "context": context,
                "error": str(e),
                "status": "error"
            })
            raise
            
    async def improve_code(self, current_code: str, improvement_type: str, 
                          context: Optional[Dict[str, Any]] = None) -> str:
        """Улучшение существующего кода"""
        try:
            # Форматируем промпт для улучшения
            formatted_prompt = self._format_improvement_prompt(
                current_code, improvement_type, context
            )
            
            # Генерируем улучшенный код
            improved_code = await self.generate_code(formatted_prompt, context)
            
            # Проверяем улучшение
            if not self._validate_improvement(current_code, improved_code):
                self.logger.warning("Улучшение не прошло валидацию")
                return current_code
                
            return improved_code
            
        except Exception as e:
            self.logger.error(f"Ошибка улучшения кода: {e}")
            return current_code
            
    def _format_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Форматирование промпта"""
        formatted = f"Задача: {prompt}\n\n"
        
        if context:
            formatted += "Контекст:\n"
            for key, value in context.items():
                formatted += f"{key}: {value}\n"
                
        formatted += "\nСгенерируйте код на Python:\n"
        return formatted
        
    def _format_improvement_prompt(self, current_code: str, improvement_type: str,
                                 context: Optional[Dict[str, Any]] = None) -> str:
        """Форматирование промпта для улучшения кода"""
        formatted = f"Текущий код:\n{current_code}\n\n"
        formatted += f"Тип улучшения: {improvement_type}\n\n"
        
        if context:
            formatted += "Контекст:\n"
            for key, value in context.items():
                formatted += f"{key}: {value}\n"
                
        formatted += "\nУлучшите код, сохраняя его функциональность:\n"
        return formatted
        
    def _validate_improvement(self, original_code: str, improved_code: str) -> bool:
        """Проверка улучшения кода"""
        try:
            # Проверяем синтаксис
            ast.parse(improved_code)
            
            # Проверяем сложность
            original_complexity = self._calculate_complexity(original_code)
            improved_complexity = self._calculate_complexity(improved_code)
            
            if improved_complexity > original_complexity * 1.5:
                self.logger.warning("Улучшенный код слишком сложный")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации улучшения: {e}")
            return False
            
    def _calculate_complexity(self, code: str) -> int:
        """Расчет сложности кода"""
        try:
            tree = ast.parse(code)
            complexity = 1  # Базовая сложность
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                   ast.AsyncWith, ast.ExceptHandler)):
                    complexity += 1
                    
            return complexity
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета сложности: {e}")
            return 0
            
    def get_generation_history(self) -> List[Dict[str, Any]]:
        """Получение истории генерации"""
        return self.generation_history 