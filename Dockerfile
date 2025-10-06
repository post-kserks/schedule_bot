# Dockerfile for Schedule Bot
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p /app/data /app/logs

# Создаем пользователя для безопасности (не root)
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Указываем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Команда для запуска бота
CMD ["python", "bot.py"]