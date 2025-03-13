from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import hashlib
import time
from datetime import datetime

class Block(BaseModel):
    """Блок изменений в системе"""
    timestamp: datetime
    node_id: str
    changes: Dict[str, Any]
    previous_hash: str
    hash: str
    validators: List[str]
    status: str = "pending"  # pending, validated, rejected

class Consensus:
    """Система консенсуса для валидации изменений"""
    
    def __init__(self, min_validators: int = 3):
        self.min_validators = min_validators
        self.blocks: List[Block] = []
        self.validators: List[str] = []
    
    def add_validator(self, node_id: str) -> None:
        """Добавление валидатора"""
        if node_id not in self.validators:
            self.validators.append(node_id)
    
    def create_block(self, node_id: str, changes: Dict[str, Any]) -> Block:
        """Создание нового блока изменений"""
        previous_hash = self.blocks[-1].hash if self.blocks else "0" * 64
        timestamp = datetime.now()
        
        # Создаем хеш блока
        block_data = f"{timestamp}{node_id}{str(changes)}{previous_hash}"
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        block = Block(
            timestamp=timestamp,
            node_id=node_id,
            changes=changes,
            previous_hash=previous_hash,
            hash=block_hash,
            validators=[]
        )
        
        self.blocks.append(block)
        return block
    
    def validate_block(self, block_hash: str, validator_id: str) -> bool:
        """Валидация блока"""
        block = next((b for b in self.blocks if b.hash == block_hash), None)
        if not block:
            return False
        
        if validator_id not in block.validators:
            block.validators.append(validator_id)
            
            # Если достигнуто минимальное количество валидаторов
            if len(block.validators) >= self.min_validators:
                block.status = "validated"
                return True
        
        return False
    
    def get_validated_changes(self) -> List[Dict[str, Any]]:
        """Получение валидированных изменений"""
        return [
            block.changes 
            for block in self.blocks 
            if block.status == "validated"
        ]
    
    def get_pending_changes(self) -> List[Dict[str, Any]]:
        """Получение ожидающих валидации изменений"""
        return [
            block.changes 
            for block in self.blocks 
            if block.status == "pending"
        ]
    
    def reject_block(self, block_hash: str) -> None:
        """Отклонение блока"""
        block = next((b for b in self.blocks if b.hash == block_hash), None)
        if block:
            block.status = "rejected" 