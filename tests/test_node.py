import pytest
import torch
from src.core.node import Node, NodeState

def test_node_creation():
    """Тест создания узла"""
    node_id = "test_node"
    position = [0.0, 0.0]
    node = Node(node_id, position)
    
    assert isinstance(node.state, NodeState)
    assert node.state.id == node_id
    assert node.state.position == position
    assert node.state.energy == 1.0
    assert isinstance(node.model, torch.nn.Module)

def test_node_state_update():
    """Тест обновления состояния узла"""
    node = Node("test_node", [0.0, 0.0])
    new_state = {
        "energy": 0.8,
        "position": [1.0, 1.0]
    }
    
    node.update_state(new_state)
    
    assert node.state.energy == 0.8
    assert node.state.position == [1.0, 1.0]

def test_node_processing():
    """Тест обработки данных узлом"""
    node = Node("test_node", [0.0, 0.0])
    input_data = torch.randn(128)
    
    output = node.process_input(input_data)
    
    assert isinstance(output, torch.Tensor)
    assert output.shape[0] == 16  # Размер выходного слоя

def test_node_communication():
    """Тест коммуникации между узлами"""
    node1 = Node("node1", [0.0, 0.0])
    node2 = Node("node2", [1.0, 1.0])
    
    message = node1.communicate(node2)
    
    assert message["source"] == "node1"
    assert message["target"] == "node2"
    assert isinstance(message["data"], dict) 