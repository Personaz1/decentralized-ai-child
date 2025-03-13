from typing import Dict, List, Optional, Union
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from pydantic import BaseModel
import numpy as np
from .consensus import Consensus, Block
import time
from datasets import Dataset
import json

class GemmaNodeState(BaseModel):
    """Состояние узла с Gemma"""
    id: str
    position: List[float]
    energy: float
    memory: Dict[str, any]
    connections: List[str]
    model_name: str = "google/gemma-2b"
    experience: List[Dict[str, any]] = []
    validation_count: int = 0
    is_validator: bool = False
    performance_metrics: Dict[str, float] = {
        "response_quality": 0.0,
        "learning_rate": 0.0,
        "validation_success": 0.0
    }

class GemmaNode:
    """Узел на базе Gemma"""
    
    def __init__(self, node_id: str, position: List[float], model_name: Optional[str] = None):
        self.state = GemmaNodeState(
            id=node_id,
            position=position,
            energy=1.0,
            memory={},
            connections=[],
            model_name=model_name or "google/gemma-2b"
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._initialize_model()
        self.consensus = Consensus()
        self.consensus.add_validator(node_id)
        self.state.is_validator = True
        self.initial_weights = self._get_model_weights()
    
    def _initialize_model(self):
        """Инициализация модели и токенизатора"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.state.model_name)
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.state.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            load_in_4bit=True,
            use_cache=True
        )
        
        # Настройка для fine-tuning
        self.training_args = TrainingArguments(
            output_dir=f"models/{self.state.id}",
            num_train_epochs=1,  # Уменьшаем для быстрого обучения
            per_device_train_batch_size=2,
            gradient_accumulation_steps=2,
            learning_rate=1e-5,
            fp16=True,
            save_strategy="epoch",
            evaluation_strategy="epoch",
            logging_steps=10,
            warmup_steps=5,
            max_steps=50
        )
    
    def _get_model_weights(self) -> Dict[str, torch.Tensor]:
        """Получение текущих весов модели"""
        return {k: v.clone() for k, v in self.model.state_dict().items()}
    
    def _prepare_training_data(self, experience: Dict[str, any]) -> Dataset:
        """Подготовка данных для обучения"""
        # Создаем пары вход-выход из опыта
        examples = []
        
        # Добавляем текущий опыт
        if "message" in experience:
            examples.append({
                "input": f"Узел {experience['source']} общается с узлом {experience['target']}",
                "output": experience["message"]
            })
        
        # Добавляем исторический опыт
        for exp in self.state.experience[-5:]:  # Используем последние 5 опытов
            if "message" in exp:
                examples.append({
                    "input": f"Узел {exp['source']} общается с узлом {exp['target']}",
                    "output": exp["message"]
                })
        
        # Создаем датасет
        dataset = Dataset.from_list(examples)
        
        # Токенизируем данные
        def tokenize_function(examples):
            inputs = self.tokenizer(
                examples["input"],
                padding="max_length",
                truncation=True,
                max_length=128
            )
            outputs = self.tokenizer(
                examples["output"],
                padding="max_length",
                truncation=True,
                max_length=128
            )
            return {
                "input_ids": inputs["input_ids"],
                "attention_mask": inputs["attention_mask"],
                "labels": outputs["input_ids"]
            }
        
        return dataset.map(tokenize_function, batched=True)
    
    def _fine_tune(self, training_data: Dataset) -> None:
        """Fine-tuning модели"""
        # Сохраняем веса до обучения
        pre_training_weights = self._get_model_weights()
        
        # Создаем тренера
        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=training_data
        )
        
        # Обучаем модель
        trainer.train()
        
        # Оцениваем качество обучения
        self._evaluate_training(pre_training_weights)
    
    def _evaluate_training(self, pre_training_weights: Dict[str, torch.Tensor]) -> None:
        """Оценка качества обучения"""
        # Сравниваем веса до и после обучения
        weight_changes = {}
        for k in pre_training_weights:
            current_weights = self.model.state_dict()[k]
            weight_diff = torch.mean(torch.abs(current_weights - pre_training_weights[k]))
            weight_changes[k] = weight_diff.item()
        
        # Обновляем метрики
        self.state.performance_metrics["learning_rate"] = np.mean(list(weight_changes.values()))
    
    def _get_model_updates(self) -> Dict[str, any]:
        """Получение обновлений модели"""
        current_weights = self._get_model_weights()
        updates = {}
        
        for k in self.initial_weights:
            updates[k] = torch.mean(torch.abs(current_weights[k] - self.initial_weights[k])).item()
        
        return {
            "weight_updates": updates,
            "performance_metrics": self.state.performance_metrics
        }
    
    def learn_from_experience(self, experience: Dict[str, any]) -> Block:
        """Обучение на основе опыта и создание блока изменений"""
        # Добавляем опыт в историю
        self.state.experience.append(experience)
        
        # Подготовка данных для fine-tuning
        training_data = self._prepare_training_data(experience)
        
        # Fine-tuning модели
        self._fine_tune(training_data)
        
        # Создаем блок изменений
        changes = {
            "experience": experience,
            "model_updates": self._get_model_updates(),
            "timestamp": experience.get("timestamp", time.time())
        }
        
        return self.consensus.create_block(self.state.id, changes)
    
    def validate_changes(self, block: Block) -> bool:
        """Валидация изменений"""
        if not self.state.is_validator:
            return False
        
        # Проверяем изменения
        if self._validate_changes(block.changes):
            self.state.validation_count += 1
            self.state.performance_metrics["validation_success"] += 1
            return self.consensus.validate_block(block.hash, self.state.id)
        
        return False
    
    def _validate_changes(self, changes: Dict[str, any]) -> bool:
        """Проверка корректности изменений"""
        # Проверяем качество обновлений
        if "model_updates" in changes:
            updates = changes["model_updates"]
            
            # Проверяем, что изменения не слишком большие
            if "weight_updates" in updates:
                max_update = max(updates["weight_updates"].values())
                if max_update > 1.0:  # Если изменения слишком большие
                    return False
            
            # Проверяем метрики производительности
            if "performance_metrics" in updates:
                metrics = updates["performance_metrics"]
                if metrics.get("learning_rate", 0) > 0.1:  # Если скорость обучения слишком высокая
                    return False
        
        return True
    
    def process_input(self, input_text: str, max_length: int = 512) -> str:
        """Обработка текстового ввода"""
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Оцениваем качество ответа
        self._evaluate_response_quality(response)
        
        return response
    
    def _evaluate_response_quality(self, response: str) -> None:
        """Оценка качества ответа"""
        # Простая метрика: длина ответа и наличие ключевых слов
        quality_score = min(1.0, len(response) / 100)  # Нормализуем по длине
        
        # Обновляем метрику
        self.state.performance_metrics["response_quality"] = (
            0.9 * self.state.performance_metrics["response_quality"] + 
            0.1 * quality_score
        )
    
    def communicate(self, target_node: 'GemmaNode') -> Dict[str, any]:
        """Коммуникация с другим узлом"""
        context = f"Узел {self.state.id} общается с узлом {target_node.state.id}"
        response = self.process_input(context)
        
        # Создаем опыт из коммуникации
        experience = {
            "type": "communication",
            "source": self.state.id,
            "target": target_node.state.id,
            "message": response,
            "timestamp": time.time(),
            "quality_score": self.state.performance_metrics["response_quality"]
        }
        
        # Обучаемся на опыте
        block = self.learn_from_experience(experience)
        
        return {
            "source": self.state.id,
            "target": target_node.state.id,
            "data": {
                "message": response,
                "block_hash": block.hash,
                "timestamp": time.time(),
                "quality_score": experience["quality_score"]
            }
        }
    
    def save_state(self, path: str) -> None:
        """Сохранение состояния узла"""
        torch.save({
            'model_state': self.model.state_dict(),
            'node_state': self.state.dict(),
            'consensus_state': self.consensus.dict(),
            'performance_metrics': self.state.performance_metrics
        }, path)
    
    def load_state(self, path: str) -> None:
        """Загрузка состояния узла"""
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state'])
        self.state = GemmaNodeState(**checkpoint['node_state'])
        self.consensus = Consensus(**checkpoint['consensus_state'])
        self.state.performance_metrics = checkpoint['performance_metrics'] 