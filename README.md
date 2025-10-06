# 📚 Telegram Bot: Расписание занятий

Умный Telegram бот для управления расписанием занятий с функциями уведомлений, контрольных мероприятий и удобным интерфейсом.

## 🚀 Быстрый старт

### Предварительные требования

- **Docker и Docker Compose** (рекомендуется для продакшн)
- **Python 3.11+** (для локальной разработки)
- **Telegram аккаунт** с токеном бота от [@BotFather](https://t.me/BotFather)

### Быстрый запуск (рекомендуемый способ)

```bash
# Клонируйте репозиторий
git clone https://github.com/post-kserks/schedule_bot.git
cd schedule_bot

# Настройте конфигурацию
cp .env.example .env
# Отредактируйте .env - добавьте BOT_TOKEN и ADMIN_USERNAMES

# Запустите автоматическое развертывание
chmod +x build-and-run.sh
./build-and-run.sh
```

## 🐳 Развертывание с Docker

### Конфигурация

Создайте файл `.env`:

```env
# Токен бота от @BotFather
BOT_TOKEN=your_actual_bot_token_here

# Username администраторов через запятую
ADMIN_USERNAMES=username1,username2,username3
```

**Получение BOT_TOKEN:**
1. Напишите [@BotFather](https://t.me/BotFather) в Telegram
2. Используйте команду `/newbot`
3. Следуйте инструкциям и получите токен
4. Вставьте токен в `.env`

### Автоматическое развертывание

```bash
# Использование скрипта (рекомендуется)
./build-and-run.sh
```

Скрипт автоматически:
- ✅ Проверяет наличие `.env`
- ✅ Создает из примера если нужно
- ✅ Останавливает старые контейнеры
- ✅ Собирает новый образ
- ✅ Запускает контейнер с правильными настройками

### Docker Compose (альтернативный способ)

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Запуск с просмотром логов
docker-compose up

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Перезапуск
docker-compose restart

# Просмотр статуса
docker-compose ps
```

### Ручное управление контейнером

```bash
# Сборка и запуск
docker build -t schedule-bot .
docker run -d --name schedule-bot --restart unless-stopped --env-file .env -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs schedule-bot

# Управление
docker ps                          # Статус
docker logs -f schedule-bot        # Логи
docker stop schedule-bot           # Остановка
docker start schedule-bot          # Запуск
docker restart schedule-bot        # Перезапуск
docker rm -f schedule-bot          # Удаление
```

## 🔧 Локальная разработка

### Установка

```bash
# Создание виртуального окружения
python -m venv venv

# Активация
source venv/bin/activate          # Linux/MacOS
venv\Scripts\activate            # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка
cp .env.example .env
# Настройте .env

# Запуск
python bot.py
```

### Зависимости для разработки

```bash
# Дополнительные зависимости для тестирования и разработки
pip install pytest pytest-asyncio
pip install black flake8 mypy     # Форматирование и линтинг
```

## 👥 Управление администраторами

### Настройка администраторов

В `.env` укажите username через запятую:

```env
ADMIN_USERNAMES=username1,username2,username3
```

**Формат:** С @ или без, система автоматически обработает.

### Проверка прав

Администраторы могут:
- Использовать `/myinfo` для проверки статуса
- Видеть кнопку "⚙️ Админ-панель"
- Управлять контрольными мероприятиями
- Просматривать список всех админов

## 🤖 Взаимодействие с ботом

### Команды

- **`/start`** - Активация и клавиатура
- **`/help`** - Справка
- **`/today`** - Расписание на сегодня
- **`/tomorrow`** - Расписание на завтра
- **`/week`** - Расписание на неделю
- **`/myinfo`** - Информация о пользователе
- **`/admin`** - Админ-панель (только для админов)

### Кнопки

**Обычные пользователи:**
```
[📅 Сегодня] [📆 Завтра]
[📅 Неделя] [❓ Помощь]
```

**Администраторы:**
```
[📅 Сегодня] [📆 Завтра]
[📅 Неделя] [❓ Помощь]
[⚙️ Админ-панель]
```

### Автоматические уведомления

- **🕘 21:00 ежедневно** - расписание на завтра
- **🔔 За 10 минут до занятия** - напоминание

## ⚙️ Административные функции

### Админ-панель

1. **📋 Список мероприятий** - все контрольные мероприятия
2. **➕ Добавить мероприятие** - пошаговое создание
3. **❌ Удалить мероприятие** - управление существующими
4. **👥 Список админов** - текущие администраторы

### Процесс добавления мероприятия

1. Дата в формате `ГГГГ-ММ-ДД`
2. Название предмета
3. Тип мероприятия (контрольная, домашняя работа и т.д.)

## 🔧 Настройка расписания

### Основные настройки

В `schedule.py` настройте:

```python
# Дата начала семестра
self.semester_start = datetime(2024, 9, 1)

# Логика числитель/знаменатель
def is_numerator_week(self, date: datetime = None) -> bool:
    week_number = delta.days // 7
    return week_number % 2 == 0  # Настройте под ваше расписание
```

### Редактирование предметов

В методах `_parse_numerator_schedule()` и `_parse_denominator_schedule()`:

```python
Subject(
    name="Название предмета",
    room="Аудитория", 
    start_time="10:10",
    end_time="11:40", 
    lesson_type="лекция/семинар/лабораторная"
)
```

**Пример:**
```python
Subject("Математический анализ", "301х", "10:10", "11:40", "лекция")
```

### Формат вывода

```
📅 Понедельник (Числитель)

🕒 10:10-11:40
📚 Математический анализ
🏫 301х
📝 лекция 🚨 Контрольная работа
```

## 🗂️ Структура проекта

```
schedule_bot/
├── 📁 data/                 # База данных (создается автоматически)
├── 📁 logs/                 # Логи приложения
├── 🐍 bot.py               # Основной логики бота
├── 🐍 config.py            # Конфигурация
├── 🐍 database.py          # Работа с БД
├── 🐍 schedule.py          # Логика расписания
├── 🐍 notifier.py          # Система уведомлений
├── 🐍 admin.py             # Админ-панель
├── 📄 requirements.txt     # Зависимости Python
├── 📄 .env                 # Конфигурация (создается)
├── 📄 .env.example         # Пример конфигурации
├── 🐳 Dockerfile           # Конфигурация Docker
├── 📄 docker-compose.yml   # Docker Compose
├── 📄 build-and-run.sh     # Скрипт автоматического развертывания
└── 📄 README.md            # Документация
```

## 🛠️ Разработка

### Тестирование

```bash
# Базовые тесты
python test_bot.py

# Тестирование модулей
python -c "from database import db; print('БД: OK')"
python -c "from schedule import schedule_manager; print('Расписание: OK')"
```

### Добавление новых функций

1. Создайте feature ветку
2. Реализуйте функционал
3. Добавьте тесты
4. Создайте Pull Request

### Code Style

```bash
# Форматирование
black bot.py admin.py schedule.py

# Линтинг
flake8 bot.py admin.py schedule.py

# Проверка типов
mypy bot.py admin.py schedule.py
```

## 🐛 Решение проблем

### Частые проблемы

**Бот не отвечает:**
- Проверьте токен в `.env`
- Убедитесь, что бот не заблокирован
- Проверьте логи: `docker logs schedule-bot`

**Нет уведомлений:**
- Проверьте время системы
- Убедитесь, что контейнер работает
- Проверьте настройки JobQueue

**Проблемы с правами:**
- Проверьте username в `.env`
- Используйте `/myinfo` для проверки статуса
- Убедитесь в отсутствии опечаток

### Диагностика

```bash
# Полная диагностика
docker logs schedule-bot | tail -50
docker exec schedule-bot python -c "
from database import db
from schedule import schedule_manager  
print('Все системы: OK')
"
```

### Мониторинг

```bash
# Использование ресурсов
docker stats schedule-bot

# Размер логов
du -sh logs/

# Размер БД
du -sh data/
```

## 📦 Продакшн рекомендации

### Безопасность

- Никогда не коммитьте `.env`
- Используйте разные токены для dev/prod
- Регулярно обновляйте зависимости
- Настройте бэкапы

### Бэкапы

```bash
# База данных
cp data/schedule.db backup/schedule_$(date +%Y%m%d).db

# Логи
tar -czf logs/backup/logs_$(date +%Y%m%d).tar.gz logs/
```

### Мониторинг

```bash
# Автоматическая проверка здоровья
# Добавьте в crontab:
# */5 * * * * docker ps | grep schedule-bot || ./build-and-run.sh
```

## 📄 Лицензия

Проект распространяется под лицензией MIT. Подробнее в файле [LICENSE](LICENSE).

## 🤝 Вклад в проект

Мы приветствуем вклад!

1. Форкните репозиторий
2. Создайте feature ветку
3. Внесите изменения
4. Создайте Pull Request

## 📞 Поддержка

При проблемах:

1. Изучите логи: `docker logs schedule-bot`
2. Проверьте конфигурацию `.env`
3. Создайте Issue на GitHub с описанием проблемы

---

**🎓 Успешного использования бота!**

---

