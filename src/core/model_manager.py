from typing import Dict, Optional, Union, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
from PIL import Image
import numpy as np
import logging
from pathlib import Path
import json
import asyncio
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ModelConfig:
    """Конфигурация модели"""
    name: str
    type: str
    version: str
    device: str
    dtype: str
    max_length: int
    batch_size: int
    temperature: float
    top_p: float
    load_in_8bit: bool
    load_in_4bit: bool

class ModelManager:
    """Управление моделями в системе"""
    
    def __init__(self, config_path: str = "config/model_config.yaml"):
        self.models: Dict[str, Any] = {
            'text': None,
            'vision': None,
            'audio': None
        }
        self.tokenizers: Dict[str, Any] = {}
        self.processors: Dict[str, Any] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        
        # Создаем директории для сохранения
        self.save_dir = Path("models/saved")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем конфигурации
        self._load_configs()
    
    def _load_configs(self):
        """Загрузка конфигураций моделей"""
        import yaml
        with open(self.config_path, 'r') as f:
            configs = yaml.safe_load(f)
        
        for model_type, config in configs.items():
            self.model_configs[model_type] = ModelConfig(**config)
    
    async def load_model(self, model_type: str, model_name: Optional[str] = None) -> None:
        """Загрузка модели"""
        if model_type not in self.model_configs:
            raise ValueError(f"Неизвестный тип модели: {model_type}")
        
        config = self.model_configs[model_type]
        model_name = model_name or config.name
        
        self.logger.info(f"Загрузка модели {model_name} типа {model_type}")
        
        try:
            if model_type == 'text':
                await self._load_text_model(model_name, config)
            elif model_type == 'vision':
                await self._load_vision_model(model_name, config)
            elif model_type == 'audio':
                await self._load_audio_model(model_name, config)
            
            self.logger.info(f"Модель {model_name} успешно загружена")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки модели {model_name}: {e}")
            raise
    
    async def _load_text_model(self, model_name: str, config: ModelConfig) -> None:
        """Загрузка текстовой модели"""
        # Загружаем токенизатор
        self.tokenizers['text'] = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        # Настройки для оптимизации памяти
        model_kwargs = {
            "device_map": "auto",
            "load_in_8bit": config.load_in_8bit,
            "load_in_4bit": config.load_in_4bit,
            "torch_dtype": getattr(torch, config.dtype)
        }
        
        # Загружаем модель
        self.models['text'] = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            **model_kwargs
        )
    
    async def _load_vision_model(self, model_name: str, config: ModelConfig) -> None:
        """Загрузка мультимодальной модели"""
        # Загружаем процессор
        self.processors['vision'] = AutoProcessor.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        # Настройки для оптимизации памяти
        model_kwargs = {
            "device_map": "auto",
            "load_in_8bit": config.load_in_8bit,
            "load_in_4bit": config.load_in_4bit,
            "torch_dtype": getattr(torch, config.dtype)
        }
        
        # Загружаем модель
        self.models['vision'] = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            **model_kwargs
        )
    
    async def _load_audio_model(self, model_name: str, config: ModelConfig) -> None:
        """Загрузка аудио модели"""
        # TODO: Реализовать загрузку аудио модели
        pass
    
    async def process(self, model_type: str, input_data: Union[str, Image.Image, np.ndarray]) -> str:
        """Обработка входных данных"""
        if model_type not in self.models:
            raise ValueError(f"Модель типа {model_type} не загружена")
        
        try:
            if model_type == 'text':
                return await self._process_text(input_data)
            elif model_type == 'vision':
                return await self._process_vision(input_data)
            elif model_type == 'audio':
                return await self._process_audio(input_data)
        except Exception as e:
            self.logger.error(f"Ошибка обработки данных: {e}")
            raise
    
    async def _process_text(self, text: str) -> str:
        """Обработка текста"""
        inputs = self.tokenizers['text'](
            text,
            return_tensors="pt",
            max_length=self.model_configs['text'].max_length,
            truncation=True
        ).to(self.models['text'].device)
        
        outputs = self.models['text'].generate(
            **inputs,
            max_length=self.model_configs['text'].max_length,
            temperature=self.model_configs['text'].temperature,
            top_p=self.model_configs['text'].top_p,
            do_sample=True
        )
        
        return self.tokenizers['text'].decode(outputs[0], skip_special_tokens=True)
    
    async def _process_vision(self, image: Image.Image) -> str:
        """Обработка изображения"""
        inputs = self.processors['vision'](
            images=image,
            return_tensors="pt"
        ).to(self.models['vision'].device)
        
        outputs = self.models['vision'].generate(
            **inputs,
            max_length=self.model_configs['vision'].max_length,
            temperature=self.model_configs['vision'].temperature,
            top_p=self.model_configs['vision'].top_p,
            do_sample=True
        )
        
        return self.processors['vision'].decode(outputs[0], skip_special_tokens=True)
    
    async def _process_audio(self, audio: np.ndarray) -> str:
        """Обработка аудио"""
        # TODO: Реализовать обработку аудио
        pass
    
    async def save_model_state(self, model_type: str) -> str:
        """Сохранение состояния модели"""
        if model_type not in self.models:
            raise ValueError(f"Модель типа {model_type} не загружена")
        
        save_path = self.save_dir / f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем модель
        self.models[model_type].save_pretrained(save_path)
        
        # Сохраняем токенизатор/процессор
        if model_type == 'text':
            self.tokenizers['text'].save_pretrained(save_path)
        elif model_type == 'vision':
            self.processors['vision'].save_pretrained(save_path)
        
        return str(save_path)
    
    async def load_model_state(self, model_type: str, state_path: str) -> None:
        """Загрузка состояния модели"""
        state_path = Path(state_path)
        if not state_path.exists():
            raise ValueError(f"Путь {state_path} не существует")
        
        # Загружаем модель
        self.models[model_type] = AutoModelForCausalLM.from_pretrained(
            state_path,
            device_map="auto",
            load_in_8bit=self.model_configs[model_type].load_in_8bit,
            load_in_4bit=self.model_configs[model_type].load_in_4bit,
            torch_dtype=getattr(torch, self.model_configs[model_type].dtype)
        )
        
        # Загружаем токенизатор/процессор
        if model_type == 'text':
            self.tokenizers['text'] = AutoTokenizer.from_pretrained(state_path)
        elif model_type == 'vision':
            self.processors['vision'] = AutoProcessor.from_pretrained(state_path)
    
    async def update_model(self, model_type: str, new_model_name: str) -> None:
        """Обновление модели на новую версию"""
        self.logger.info(f"Обновление модели {model_type} на {new_model_name}")
        
        try:
            # Сохраняем текущее состояние
            current_state = await self.save_model_state(model_type)
            
            # Загружаем новую модель
            await self.load_model(model_type, new_model_name)
            
            # Обновляем конфигурацию
            self.model_configs[model_type].name = new_model_name
            self.model_configs[model_type].version = new_model_name.split('/')[-1]
            
            self.logger.info(f"Модель {model_type} успешно обновлена")
        except Exception as e:
            self.logger.error(f"Ошибка обновления модели: {e}")
            # Восстанавливаем предыдущее состояние
            await self.load_model_state(model_type, current_state)
            raise 