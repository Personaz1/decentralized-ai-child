import uvicorn
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/web_server.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Запуск веб-сервера"""
    try:
        # Создаем директорию для логов, если её нет
        Path("logs").mkdir(exist_ok=True)
        
        # Запускаем сервер
        uvicorn.run(
            "web.server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}")
        raise

if __name__ == "__main__":
    main() 