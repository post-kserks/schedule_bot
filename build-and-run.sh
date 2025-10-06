#!/bin/bash

# Скрипт для сборки и запуска бота в Docker

# Создаем .env файл из примера если его нет
if [ ! -f .env ]; then
    echo "Создаю .env файл из примера..."
    cp .env.example .env
    echo "Пожалуйста, отредактируйте .env файл и добавьте BOT_TOKEN и ADMIN_USERNAME"
    exit 1
fi

# Собираем Docker образ
echo "Сборка Docker образа..."
docker build -t schedule-bot .

# Запускаем контейнер
echo "Запуск контейнера..."
docker run -d \
    --name schedule-bot \
    --restart unless-stopped \
    --env-file .env \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/logs:/app/logs \
    schedule-bot

echo "Бот запущен! Проверьте логи: docker logs schedule-bot"