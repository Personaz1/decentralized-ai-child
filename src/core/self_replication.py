import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import numpy as np
from datetime import datetime
import shutil

class ReplicationType(Enum):
    """Типы репликации"""
    FULL = "full"  # Полная репликация
    PARTIAL = "partial"  # Частичная репликация
    SPECIALIZED = "specialized"  # Специализированная репликация
    EXPERIMENTAL = "experimental"  # Экспериментальная репликация

@dataclass
class ReplicationConfig:
    """Конфигурация репликации"""
    replication_type: ReplicationType
    parent_node: str
    capabilities: Dict[str, float]
    specialization: Optional[str] = None
    experimental_params: Optional[Dict[str, Any]] = None

class SelfReplicationSystem:
    """Система саморепликации"""
    
    def __init__(self, config_path: str = "config/system_config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.replications: List[Dict] = []
        self.active_replicas: Dict[str, Dict] = {}
        
        # Создаем директорию для хранения репликаций
        self.replication_dir = Path("replication_history")
        self.replication_dir.mkdir(exist_ok=True)
    
    async def create_replica(self, config: ReplicationConfig) -> Optional[str]:
        """Создание реплики узла"""
        try:
            # Генерируем уникальный ID
            replica_id = f"replica_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Создаем реплику в зависимости от типа
            if config.replication_type == ReplicationType.FULL:
                await self._create_full_replica(replica_id, config)
            elif config.replication_type == ReplicationType.PARTIAL:
                await self._create_partial_replica(replica_id, config)
            elif config.replication_type == ReplicationType.SPECIALIZED:
                await self._create_specialized_replica(replica_id, config)
            elif config.replication_type == ReplicationType.EXPERIMENTAL:
                await self._create_experimental_replica(replica_id, config)
            
            # Сохраняем информацию о репликации
            replication_info = {
                "replica_id": replica_id,
                "parent_node": config.parent_node,
                "replication_type": config.replication_type.value,
                "capabilities": config.capabilities,
                "specialization": config.specialization,
                "experimental_params": config.experimental_params,
                "creation_timestamp": datetime.now(),
                "status": "active"
            }
            
            self.replications.append(replication_info)
            self.active_replicas[replica_id] = replication_info
            
            # Сохраняем информацию
            await self._save_replication(replication_info)
            
            return replica_id
            
        except Exception as e:
            self.logger.error(f"Ошибка создания реплики: {e}")
            return None
    
    async def _create_full_replica(self, replica_id: str, config: ReplicationConfig):
        """Создание полной реплики"""
        # Копируем все файлы и директории
        parent_dir = Path(f"nodes/{config.parent_node}")
        replica_dir = Path(f"nodes/{replica_id}")
        
        if parent_dir.exists():
            shutil.copytree(parent_dir, replica_dir)
            
            # Обновляем конфигурацию реплики
            config_file = replica_dir / "config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    replica_config = json.load(f)
                
                replica_config["node_id"] = replica_id
                replica_config["capabilities"] = config.capabilities
                
                with open(config_file, 'w') as f:
                    json.dump(replica_config, f)
    
    async def _create_partial_replica(self, replica_id: str, config: ReplicationConfig):
        """Создание частичной реплики"""
        # Копируем только необходимые компоненты
        parent_dir = Path(f"nodes/{config.parent_node}")
        replica_dir = Path(f"nodes/{replica_id}")
        
        if parent_dir.exists():
            replica_dir.mkdir(parents=True, exist_ok=True)
            
            # Копируем основные компоненты
            essential_files = ["model", "config.json", "knowledge_base"]
            for file in essential_files:
                src = parent_dir / file
                if src.exists():
                    if src.is_file():
                        shutil.copy2(src, replica_dir)
                    else:
                        shutil.copytree(src, replica_dir / file)
    
    async def _create_specialized_replica(self, replica_id: str, config: ReplicationConfig):
        """Создание специализированной реплики"""
        # Создаем реплику с определенной специализацией
        parent_dir = Path(f"nodes/{config.parent_node}")
        replica_dir = Path(f"nodes/{replica_id}")
        
        if parent_dir.exists():
            replica_dir.mkdir(parents=True, exist_ok=True)
            
            # Копируем базовые компоненты
            await self._create_partial_replica(replica_id, config)
            
            # Добавляем специализацию
            specialization_dir = replica_dir / "specialization"
            specialization_dir.mkdir(exist_ok=True)
            
            # Сохраняем информацию о специализации
            with open(specialization_dir / "config.json", 'w') as f:
                json.dump({
                    "type": config.specialization,
                    "capabilities": config.capabilities,
                    "timestamp": datetime.now().isoformat()
                }, f)
    
    async def _create_experimental_replica(self, replica_id: str, config: ReplicationConfig):
        """Создание экспериментальной реплики"""
        # Создаем реплику с экспериментальными параметрами
        parent_dir = Path(f"nodes/{config.parent_node}")
        replica_dir = Path(f"nodes/{replica_id}")
        
        if parent_dir.exists():
            replica_dir.mkdir(parents=True, exist_ok=True)
            
            # Копируем базовые компоненты
            await self._create_partial_replica(replica_id, config)
            
            # Добавляем экспериментальные параметры
            experimental_dir = replica_dir / "experimental"
            experimental_dir.mkdir(exist_ok=True)
            
            # Сохраняем экспериментальные параметры
            with open(experimental_dir / "params.json", 'w') as f:
                json.dump({
                    "parameters": config.experimental_params,
                    "timestamp": datetime.now().isoformat()
                }, f)
    
    async def _save_replication(self, replication_info: Dict):
        """Сохранение информации о репликации"""
        replication_file = self.replication_dir / f"replication_{replication_info['replica_id']}.json"
        with open(replication_file, 'w') as f:
            json.dump(replication_info, f)
    
    async def merge_replicas(self, replica_ids: List[str]) -> Optional[str]:
        """Объединение реплик"""
        try:
            # Проверяем существование реплик
            if not all(replica_id in self.active_replicas for replica_id in replica_ids):
                return None
            
            # Создаем новую реплику на основе объединения
            merged_id = f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            merged_dir = Path(f"nodes/{merged_id}")
            merged_dir.mkdir(parents=True, exist_ok=True)
            
            # Объединяем знания и опыт
            merged_knowledge = []
            merged_capabilities = {}
            
            for replica_id in replica_ids:
                replica = self.active_replicas[replica_id]
                knowledge_dir = Path(f"nodes/{replica_id}/knowledge_base")
                if knowledge_dir.exists():
                    merged_knowledge.extend(self._load_knowledge(knowledge_dir))
                
                # Объединяем возможности
                for capability, value in replica["capabilities"].items():
                    if capability not in merged_capabilities:
                        merged_capabilities[capability] = value
                    else:
                        merged_capabilities[capability] = max(
                            merged_capabilities[capability],
                            value
                        )
            
            # Сохраняем объединенные знания
            knowledge_dir = merged_dir / "knowledge_base"
            knowledge_dir.mkdir(exist_ok=True)
            self._save_knowledge(knowledge_dir, merged_knowledge)
            
            # Создаем конфигурацию объединенной реплики
            config = ReplicationConfig(
                replication_type=ReplicationType.SPECIALIZED,
                parent_node=replica_ids[0],
                capabilities=merged_capabilities,
                specialization="merged"
            )
            
            # Сохраняем информацию об объединении
            replication_info = {
                "replica_id": merged_id,
                "parent_nodes": replica_ids,
                "replication_type": ReplicationType.SPECIALIZED.value,
                "capabilities": merged_capabilities,
                "specialization": "merged",
                "creation_timestamp": datetime.now(),
                "status": "active"
            }
            
            self.replications.append(replication_info)
            self.active_replicas[merged_id] = replication_info
            
            await self._save_replication(replication_info)
            
            return merged_id
            
        except Exception as e:
            self.logger.error(f"Ошибка объединения реплик: {e}")
            return None
    
    def _load_knowledge(self, knowledge_dir: Path) -> List[Dict]:
        """Загрузка знаний из директории"""
        knowledge = []
        for file in knowledge_dir.glob("*.json"):
            with open(file, 'r') as f:
                knowledge.extend(json.load(f))
        return knowledge
    
    def _save_knowledge(self, knowledge_dir: Path, knowledge: List[Dict]):
        """Сохранение знаний в директорию"""
        for i, item in enumerate(knowledge):
            with open(knowledge_dir / f"knowledge_{i}.json", 'w') as f:
                json.dump(item, f)
    
    async def get_replication_history(self) -> List[Dict]:
        """Получение истории репликаций"""
        return [
            {
                "replica_id": r["replica_id"],
                "parent_node": r["parent_node"],
                "replication_type": r["replication_type"],
                "capabilities": r["capabilities"],
                "creation_timestamp": r["creation_timestamp"].isoformat(),
                "status": r["status"]
            }
            for r in self.replications
        ]
    
    async def get_active_replicas(self) -> List[str]:
        """Получение списка активных реплик"""
        return list(self.active_replicas.keys()) 