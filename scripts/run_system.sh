#!/bin/bash

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
echo "Установка зависимостей..."
pip install -r requirements.txt

# Создаем необходимые директории
echo "Создание директорий..."
mkdir -p models models/saved knowledge metrics logs config

# Проверяем наличие конфигурационных файлов
if [ ! -f "config/system_config.yaml" ]; then
    echo "Ошибка: config/system_config.yaml не найден"
    exit 1
fi

if [ ! -f "config/model_config.yaml" ]; then
    echo "Ошибка: config/model_config.yaml не найден"
    exit 1
fi

# Запускаем систему
echo "Запуск системы..."
python src/main.py

# Деактивируем виртуальное окружение
deactivate 