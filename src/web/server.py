from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import json
from pathlib import Path
import logging
from datetime import datetime

from core.decentralized_ai import DecentralizedAISystem

app = FastAPI(title="DecentralizedAI Web Interface")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Настраиваем шаблоны
templates = Jinja2Templates(directory="web/templates")

# Инициализируем систему
system = DecentralizedAISystem()

# OAuth2 схема для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ChatRequest(BaseModel):
    """Модель запроса чата"""
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Модель ответа чата"""
    response: str
    node_id: str
    timestamp: datetime
    metrics: Optional[Dict[str, float]] = None

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "DecentralizedAI"}
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """API для чата"""
    try:
        # Получаем доступный узел
        node = await system.get_available_node()
        
        # Отправляем сообщение
        response = await node.process_message(request.message, request.context)
        
        # Получаем метрики
        metrics = await node.get_performance_metrics()
        
        return ChatResponse(
            response=response,
            node_id=node.node_id,
            timestamp=datetime.now(),
            metrics=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/status")
async def get_system_status():
    """Получение статуса системы"""
    return {
        "active_nodes": len(system.nodes),
        "total_requests": system.total_requests,
        "average_response_time": system.average_response_time,
        "system_health": system.get_system_health()
    }

@app.get("/api/nodes")
async def get_nodes():
    """Получение списка узлов"""
    return [
        {
            "node_id": node.node_id,
            "status": node.status,
            "capabilities": node.capabilities,
            "current_load": node.current_load
        }
        for node in system.nodes.values()
    ]

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket для чата"""
    await websocket.accept()
    
    try:
        while True:
            # Получаем сообщение
            message = await websocket.receive_text()
            
            # Обрабатываем сообщение
            response = await system.process_message(message)
            
            # Отправляем ответ
            await websocket.send_json({
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        await websocket.close(code=1000, reason=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """Получение метрик системы"""
    return {
        "performance": await system.get_performance_metrics(),
        "network": await system.get_network_metrics(),
        "resource_usage": await system.get_resource_usage()
    }

@app.post("/api/nodes/register")
async def register_node(node_info: Dict[str, Any]):
    """Регистрация нового узла"""
    try:
        node_id = await system.register_node(node_info)
        return {"node_id": node_id, "status": "registered"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/nodes/{node_id}")
async def unregister_node(node_id: str):
    """Удаление узла"""
    try:
        await system.unregister_node(node_id)
        return {"status": "unregistered"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 