#!/bin/bash

# Создаем виртуальное окружение, если его нет
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Запускаем тесты с покрытием
coverage run -m unittest discover tests/
coverage report
coverage html

# Открываем отчет о покрытии в браузере
open htmlcov/index.html

# Деактивируем виртуальное окружение
deactivate 