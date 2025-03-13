from typing import Dict, List, Any, Optional
import torch
import torch.nn as nn
import torch.optim as optim
from dataclasses import dataclass
import numpy as np

@dataclass
class LearningConfig:
    """Конфигурация процесса обучения"""
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 10
    loss_function: str = "mse"
    optimizer: str = "adam"

class LearningMechanism:
    """Механизм обучения для узлов"""
    
    def __init__(self, model: nn.Module, config: LearningConfig):
        self.model = model
        self.config = config
        self.optimizer = self._create_optimizer()
        self.criterion = self._create_criterion()
        
    def _create_optimizer(self) -> optim.Optimizer:
        """Создание оптимизатора"""
        if self.config.optimizer.lower() == "adam":
            return optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        elif self.config.optimizer.lower() == "sgd":
            return optim.SGD(self.model.parameters(), lr=self.config.learning_rate)
        else:
            raise ValueError(f"Unsupported optimizer: {self.config.optimizer}")
    
    def _create_criterion(self) -> nn.Module:
        """Создание функции потерь"""
        if self.config.loss_function.lower() == "mse":
            return nn.MSELoss()
        elif self.config.loss_function.lower() == "cross_entropy":
            return nn.CrossEntropyLoss()
        else:
            raise ValueError(f"Unsupported loss function: {self.config.loss_function}")
    
    def train_step(self, input_data: torch.Tensor, target_data: torch.Tensor) -> float:
        """Один шаг обучения"""
        self.optimizer.zero_grad()
        output = self.model(input_data)
        loss = self.criterion(output, target_data)
        loss.backward()
        self.optimizer.step()
        return loss.item()
    
    def train(self, train_data: List[Dict[str, torch.Tensor]]) -> List[float]:
        """Полный цикл обучения"""
        losses = []
        for epoch in range(self.config.epochs):
            epoch_loss = 0
            for batch in self._create_batches(train_data):
                loss = self.train_step(batch["input"], batch["target"])
                epoch_loss += loss
            losses.append(epoch_loss / len(train_data))
        return losses
    
    def _create_batches(self, data: List[Dict[str, torch.Tensor]]) -> List[Dict[str, torch.Tensor]]:
        """Создание батчей для обучения"""
        batches = []
        for i in range(0, len(data), self.config.batch_size):
            batch = data[i:i + self.config.batch_size]
            batches.append({
                "input": torch.stack([item["input"] for item in batch]),
                "target": torch.stack([item["target"] for item in batch])
            })
        return batches
    
    def save_model(self, path: str) -> None:
        """Сохранение модели"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config
        }, path)
    
    def load_model(self, path: str) -> None:
        """Загрузка модели"""
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.config = checkpoint['config'] 