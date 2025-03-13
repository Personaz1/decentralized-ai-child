import asyncio
import logging
from pathlib import Path
import yaml
from typing import Dict, List, Optional
from datetime import datetime
import psutil
import GPUtil
import json

from core.model_manager import ModelManager
from core.knowledge_exchange import KnowledgeExchange
from core.performance_monitor import PerformanceMonitor
from core.gemma_node import GemmaNode
from core.consensus import Consensus
from core.model_updater import ModelUpdater
from core.auto_scaler import AutoScaler
from core.backup_system import BackupSystem
from core.work_mode_manager import WorkModeManager, NodeResources, WorkMode
from core.evolutionary_consensus import EvolutionaryConsensus, ConsensusProposal, ConsensusRule
from core.network_self_organization import NetworkSelfOrganization, NodeRole
from core.ethical_system import EthicalSystem, EthicalPrinciple
from visualization.metrics_visualizer import MetricsVisualizer
from core.model_evolution import ModelEvolutionSystem
from core.conflict_prevention import ConflictPreventionSystem
from core.self_replication import SelfReplicationSystem
from core.vulnerability_detection import VulnerabilityDetectionSystem
from core.decentralized_ai import DecentralizedAISystem

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('system.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Загрузка конфигурации
        config_path = Path("config/system_config.yaml")
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Инициализация системы
        system = DecentralizedAISystem(
            system_root=Path("."),
            logger=logger,
            config=config
        )
        
        # Запуск системы
        logger.info("Запуск системы...")
        await system.start()
        
        # Ожидание завершения
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Получен сигнал завершения")
        
        # Корректное завершение
        await system.stop()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске системы: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 