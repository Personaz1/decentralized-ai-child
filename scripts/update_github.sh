#!/bin/bash

# Проверяем изменения
if git status --porcelain | grep -q '^[MADRC]'; then
    # Добавляем все изменения
    git add .
    
    # Создаем коммит с текущей датой
    commit_message="Update: $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$commit_message"
    
    # Отправляем изменения в удаленный репозиторий
    git push origin main
    
    echo "Изменения успешно отправлены в GitHub"
else
    echo "Нет изменений для коммита"
fi 