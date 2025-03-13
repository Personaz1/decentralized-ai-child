import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import numpy as np
from datetime import datetime

class ConsensusRule(Enum):
    """Типы правил консенсуса"""
    MAJORITY = "majority"
    WEIGHTED = "weighted"
    REPUTATION = "reputation"
    EVOLUTIONARY = "evolutionary"

@dataclass
class ConsensusProposal:
    """Предложение по улучшению консенсуса"""
    node_id: str
    rule_type: ConsensusRule
    parameters: Dict[str, Any]
    fitness_score: float
    timestamp: datetime
    justification: str

class EvolutionaryConsensus:
    """Эволюционный консенсус"""
    
    def __init__(self, config_path: str = "config/system_config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.proposals: List[ConsensusProposal] = []
        self.current_rule = ConsensusRule.EVOLUTIONARY
        self.node_reputation: Dict[str, float] = {}
        self.rule_history: List[Dict] = []
        
        # Создаем директорию для хранения эволюционной истории
        self.history_dir = Path("evolution_history")
        self.history_dir.mkdir(exist_ok=True)
    
    async def propose_rule(self, proposal: ConsensusProposal) -> bool:
        """Предложение нового правила консенсуса"""
        try:
            # Проверяем качество предложения
            if not await self._validate_proposal(proposal):
                return False
            
            # Добавляем предложение в список
            self.proposals.append(proposal)
            
            # Обновляем репутацию узла
            self._update_node_reputation(proposal.node_id, proposal.fitness_score)
            
            # Проверяем возможность эволюции
            await self._check_evolution()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке предложения: {e}")
            return False
    
    async def _validate_proposal(self, proposal: ConsensusProposal) -> bool:
        """Проверка предложения на валидность"""
        # Проверяем параметры
        if not self._validate_parameters(proposal.parameters):
            return False
        
        # Проверяем обоснование
        if not self._validate_justification(proposal.justification):
            return False
        
        # Проверяем репутацию узла
        if proposal.node_id in self.node_reputation:
            if self.node_reputation[proposal.node_id] < 0.5:
                return False
        
        return True
    
    def _validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Проверка параметров предложения"""
        required_params = ["threshold", "timeout", "min_validators"]
        return all(param in parameters for param in required_params)
    
    def _validate_justification(self, justification: str) -> bool:
        """Проверка обоснования предложения"""
        return len(justification) > 100 and len(justification.split()) > 20
    
    def _update_node_reputation(self, node_id: str, fitness_score: float):
        """Обновление репутации узла"""
        if node_id not in self.node_reputation:
            self.node_reputation[node_id] = 0.5
        
        # Обновляем репутацию на основе фитнес-скора
        self.node_reputation[node_id] = (
            0.7 * self.node_reputation[node_id] + 
            0.3 * fitness_score
        )
    
    async def _check_evolution(self):
        """Проверка возможности эволюции"""
        if len(self.proposals) < 5:
            return
        
        # Сортируем предложения по фитнес-скору
        sorted_proposals = sorted(
            self.proposals,
            key=lambda x: x.fitness_score,
            reverse=True
        )
        
        # Выбираем лучшие предложения
        best_proposals = sorted_proposals[:3]
        
        # Создаем новое правило на основе лучших предложений
        new_rule = await self._create_new_rule(best_proposals)
        
        # Проверяем улучшение
        if await self._evaluate_improvement(new_rule):
            # Применяем новое правило
            await self._apply_new_rule(new_rule)
            
            # Сохраняем историю
            await self._save_evolution_history(new_rule)
    
    async def _create_new_rule(self, proposals: List[ConsensusProposal]) -> Dict:
        """Создание нового правила на основе лучших предложений"""
        # Комбинируем параметры лучших предложений
        combined_params = {}
        for key in proposals[0].parameters.keys():
            values = [p.parameters[key] for p in proposals]
            combined_params[key] = np.mean(values)
        
        return {
            "rule_type": ConsensusRule.EVOLUTIONARY,
            "parameters": combined_params,
            "timestamp": datetime.now(),
            "proposals_used": [p.node_id for p in proposals]
        }
    
    async def _evaluate_improvement(self, new_rule: Dict) -> bool:
        """Оценка улучшения от нового правила"""
        # TODO: Реализовать оценку улучшения
        return True
    
    async def _apply_new_rule(self, new_rule: Dict):
        """Применение нового правила"""
        self.current_rule = new_rule["rule_type"]
        self.rule_history.append(new_rule)
        
        # Очищаем список предложений
        self.proposals = []
    
    async def _save_evolution_history(self, new_rule: Dict):
        """Сохранение истории эволюции"""
        history_file = self.history_dir / f"evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(history_file, 'w') as f:
            json.dump(new_rule, f, default=str)
    
    async def get_current_rule(self) -> Dict:
        """Получение текущего правила консенсуса"""
        return {
            "rule_type": self.current_rule.value,
            "parameters": self.rule_history[-1]["parameters"] if self.rule_history else {},
            "timestamp": self.rule_history[-1]["timestamp"] if self.rule_history else None
        }
    
    async def get_evolution_history(self) -> List[Dict]:
        """Получение истории эволюции"""
        return self.rule_history 