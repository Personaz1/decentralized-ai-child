#!/bin/bash

# Создаем задачу в crontab для обновления каждые 30 минут
(crontab -l 2>/dev/null | grep -v "update_github.sh") | crontab -
(crontab -l 2>/dev/null; echo "*/30 * * * * $(pwd)/scripts/update_github.sh >> $(pwd)/logs/github_updates.log 2>&1") | crontab -

echo "Задача обновления GitHub добавлена в crontab"
echo "Логи будут сохраняться в logs/github_updates.log" 