#!/bin/bash

# Скрипт для сборки и запуска бота в Docker

# Создаем .env файл из примера если его нет
if [ ! -f .env ]; then
    echo "Создаю .env файл из примера..."
    cp .env.example .env
    echo "Пожалуйста, отредактируйте .env файл и добавьте BOT_TOKEN и ADMIN_USERNAME"
    exit 1
fi

# Останавливаем и удаляем старый контейнер если он существует
echo "Проверка существующих контейнеров..."
if docker ps -a | grep -q schedule-bot; then
    echo "Останавливаем и удаляем старый контейнер..."
    docker stop schedule-bot >/dev/null 2>&1
    docker rm schedule-bot >/dev/null 2>&1
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

echo "Бот запущен!"
echo "Проверьте логи: docker logs -f schedule-bot"
echo "Остановить бота: docker stop schedule-bot"
echo "Перезапустить бота: docker restart schedule-bot"