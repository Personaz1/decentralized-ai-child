import asyncio
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import numpy as np
from datetime import datetime

class NodeRole(Enum):
    """Роли узлов в сети"""
    WORKER = "worker"
    VALIDATOR = "validator"
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    GUARDIAN = "guardian"

@dataclass
class NetworkMetrics:
    """Метрики сети"""
    latency: float
    bandwidth: float
    reliability: float
    load: float
    timestamp: datetime

class NetworkSelfOrganization:
    """Самоорганизация сети"""
    
    def __init__(self, config_path: str = "config/system_config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.nodes: Dict[str, Dict] = {}
        self.connections: Dict[str, Set[str]] = {}
        self.metrics: Dict[str, List[NetworkMetrics]] = {}
        self.role_history: Dict[str, List[NodeRole]] = {}
        
        # Создаем директорию для хранения топологии
        self.topology_dir = Path("network_topology")
        self.topology_dir.mkdir(exist_ok=True)
    
    async def register_node(self, node_id: str, capabilities: Dict[str, float]):
        """Регистрация нового узла"""
        try:
            self.nodes[node_id] = {
                "capabilities": capabilities,
                "role": None,
                "connections": set(),
                "last_update": datetime.now()
            }
            
            # Определяем начальную роль
            await self._assign_role(node_id)
            
            # Устанавливаем начальные соединения
            await self._establish_connections(node_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка регистрации узла {node_id}: {e}")
            return False
    
    async def _assign_role(self, node_id: str):
        """Определение роли узла"""
        capabilities = self.nodes[node_id]["capabilities"]
        
        # Анализируем возможности
        compute_power = capabilities.get("compute_power", 0)
        memory = capabilities.get("memory", 0)
        bandwidth = capabilities.get("bandwidth", 0)
        reliability = capabilities.get("reliability", 0)
        
        # Определяем роль на основе возможностей
        if compute_power > 0.8 and memory > 0.8:
            role = NodeRole.COORDINATOR
        elif reliability > 0.9:
            role = NodeRole.VALIDATOR
        elif compute_power > 0.7:
            role = NodeRole.RESEARCHER
        elif bandwidth > 0.8:
            role = NodeRole.GUARDIAN
        else:
            role = NodeRole.WORKER
        
        # Сохраняем роль
        self.nodes[node_id]["role"] = role
        if node_id not in self.role_history:
            self.role_history[node_id] = []
        self.role_history[node_id].append(role)
    
    async def _establish_connections(self, node_id: str):
        """Установка соединений с другими узлами"""
        # Находим подходящие узлы для соединения
        suitable_nodes = await self._find_suitable_nodes(node_id)
        
        # Устанавливаем соединения
        for target_id in suitable_nodes:
            await self._create_connection(node_id, target_id)
    
    async def _find_suitable_nodes(self, node_id: str) -> List[str]:
        """Поиск подходящих узлов для соединения"""
        current_role = self.nodes[node_id]["role"]
        suitable_nodes = []
        
        for target_id, target_data in self.nodes.items():
            if target_id == node_id:
                continue
                
            target_role = target_data["role"]
            
            # Определяем совместимость ролей
            if self._are_roles_compatible(current_role, target_role):
                suitable_nodes.append(target_id)
        
        return suitable_nodes[:3]  # Ограничиваем количество соединений
    
    def _are_roles_compatible(self, role1: NodeRole, role2: NodeRole) -> bool:
        """Проверка совместимости ролей"""
        compatibility_matrix = {
            NodeRole.COORDINATOR: [NodeRole.VALIDATOR, NodeRole.RESEARCHER],
            NodeRole.VALIDATOR: [NodeRole.COORDINATOR, NodeRole.WORKER],
            NodeRole.RESEARCHER: [NodeRole.COORDINATOR, NodeRole.GUARDIAN],
            NodeRole.GUARDIAN: [NodeRole.RESEARCHER, NodeRole.WORKER],
            NodeRole.WORKER: [NodeRole.VALIDATOR, NodeRole.GUARDIAN]
        }
        
        return role2 in compatibility_matrix[role1]
    
    async def _create_connection(self, node1_id: str, node2_id: str):
        """Создание соединения между узлами"""
        if node1_id not in self.connections:
            self.connections[node1_id] = set()
        if node2_id not in self.connections:
            self.connections[node2_id] = set()
        
        self.connections[node1_id].add(node2_id)
        self.connections[node2_id].add(node1_id)
        
        # Обновляем метрики соединения
        await self._update_connection_metrics(node1_id, node2_id)
    
    async def _update_connection_metrics(self, node1_id: str, node2_id: str):
        """Обновление метрик соединения"""
        # TODO: Реализовать измерение метрик
        metrics = NetworkMetrics(
            latency=0.1,
            bandwidth=100.0,
            reliability=0.95,
            load=0.1,
            timestamp=datetime.now()
        )
        
        for node_id in [node1_id, node2_id]:
            if node_id not in self.metrics:
                self.metrics[node_id] = []
            self.metrics[node_id].append(metrics)
    
    async def optimize_network(self):
        """Оптимизация топологии сети"""
        for node_id in self.nodes:
            # Анализируем текущие соединения
            current_connections = self.connections.get(node_id, set())
            
            # Находим оптимальные соединения
            optimal_connections = await self._find_suitable_nodes(node_id)
            
            # Удаляем неоптимальные соединения
            for connection in current_connections:
                if connection not in optimal_connections:
                    await self._remove_connection(node_id, connection)
            
            # Добавляем новые оптимальные соединения
            for connection in optimal_connections:
                if connection not in current_connections:
                    await self._create_connection(node_id, connection)
    
    async def _remove_connection(self, node1_id: str, node2_id: str):
        """Удаление соединения между узлами"""
        if node1_id in self.connections:
            self.connections[node1_id].discard(node2_id)
        if node2_id in self.connections:
            self.connections[node2_id].discard(node1_id)
    
    async def get_network_topology(self) -> Dict:
        """Получение текущей топологии сети"""
        return {
            "nodes": {
                node_id: {
                    "role": node_data["role"].value,
                    "connections": list(self.connections.get(node_id, set()))
                }
                for node_id, node_data in self.nodes.items()
            },
            "timestamp": datetime.now()
        }
    
    async def save_topology(self):
        """Сохранение топологии сети"""
        topology = await self.get_network_topology()
        topology_file = self.topology_dir / f"topology_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(topology_file, 'w') as f:
            json.dump(topology, f, default=str) 