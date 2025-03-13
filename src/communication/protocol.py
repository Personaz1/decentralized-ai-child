from typing import Dict, List, Any
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime

class Message(BaseModel):
    """Модель сообщения для коммуникации между узлами"""
    source_id: str
    target_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class CommunicationProtocol:
    """Протокол коммуникации между узлами"""
    
    def __init__(self):
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.subscribers: Dict[str, List[callable]] = {}
    
    async def send_message(self, message: Message) -> None:
        """Отправка сообщения"""
        await self.message_queue.put(message)
        if message.target_id in self.subscribers:
            for callback in self.subscribers[message.target_id]:
                await callback(message)
    
    async def subscribe(self, node_id: str, callback: callable) -> None:
        """Подписка на сообщения"""
        if node_id not in self.subscribers:
            self.subscribers[node_id] = []
        self.subscribers[node_id].append(callback)
    
    async def unsubscribe(self, node_id: str, callback: callable) -> None:
        """Отписка от сообщений"""
        if node_id in self.subscribers:
            self.subscribers[node_id].remove(callback)
    
    async def process_messages(self) -> None:
        """Обработка сообщений в очереди"""
        while True:
            message = await self.message_queue.get()
            try:
                # Здесь будет реализована логика обработки сообщений
                print(f"Processing message from {message.source_id} to {message.target_id}")
            except Exception as e:
                print(f"Error processing message: {e}")
            finally:
                self.message_queue.task_done()
    
    def serialize_message(self, message: Message) -> str:
        """Сериализация сообщения"""
        return json.dumps(message.dict())
    
    def deserialize_message(self, message_str: str) -> Message:
        """Десериализация сообщения"""
        return Message.parse_raw(message_str) 