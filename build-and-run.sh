#!/bin/bash

# Скрипт для сборки и запуска бота в Docker

# Создаем .env файл из примера если его нет
if [ ! -f .env ]; then
    echo "Создаю .env файл из примера..."
    cp .env.example .env
    echo "⚠️  Пожалуйста, отредактируйте .env файл и добавьте BOT_TOKEN и ADMIN_USERNAMES"
    echo "📝 Редактирование: nano .env"
    exit 1
fi

# Проверяем наличие необходимых переменных
if ! grep -q "BOT_TOKEN" .env || grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    echo "❌ BOT_TOKEN не настроен в .env файле"
    echo "📝 Получите токен у @BotFather и добавьте в .env"
    exit 1
fi

echo "🚀 Запуск бота расписания..."
echo "📦 Использование Docker Compose..."

# Запускаем с помощью docker-compose
docker-compose down 2>/dev/null
docker-compose up -d --build

echo "✅ Бот запущен!"
echo ""
echo "📊 Команды управления:"
echo "   docker-compose up --build -d - Сборка и запуск в фоновом режиме"
echo "   docker-compose logs -f       - Просмотр логов"
echo "   docker-compose down          - Остановка бота"
echo "   docker-compose restart       - Перезапуск бота"
echo "   docker-compose ps            - Статус контейнеров"
echo ""
echo "🐛 Для проверки работы отправьте боту команду /start"