# Home Assistant Telegram Bot

![CI/CD Pipeline](https://github.com/username/home-assistant-telegram-bot/workflows/CI/CD%20Pipeline/badge.svg)
![Coverage](https://codecov.io/gh/username/home-assistant-telegram-bot/branch/main/graph/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Система управления умным домом через Telegram бот с веб-интерфейсом на базе Flask.

## Возможности

- 🏠 **Home Assistant интеграция** - Полная интеграция с вашей системой умного дома
- 🤖 **Telegram бот** - Управление устройствами через Telegram с русским интерфейсом
- 🌐 **Веб-панель** - Современный веб-интерфейс для мониторинга и управления
- 📊 **Статистика в реальном времени** - Мониторинг состояния устройств и сервисов
- 🔒 **Безопасность** - Токен-авторизация и защищенные соединения

## Команды Telegram бота

- `/start` - Приветствие и список команд
- `/help` - Справка по командам
- `/status` - Статус Home Assistant
- `/lights` - Список всех световых устройств
- `/light_on <entity_id>` - Включить свет
- `/light_off <entity_id>` - Выключить свет  
- `/switches` - Список всех переключателей
- `/switch_on <entity_id>` - Включить переключатель
- `/switch_off <entity_id>` - Выключить переключатель
- `/sensors` - Показания датчиков

## Быстрый старт

### 1. Переменные окружения

Создайте файл `.env` со следующими переменными:

```env
HOME_ASSISTANT_URL=https://your-homeassistant-url.com
HOME_ASSISTANT_TOKEN=your_long_lived_access_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SESSION_SECRET=your_flask_session_secret
```

### 2. Установка зависимостей

```bash
pip install flask python-telegram-bot requests gunicorn prometheus-client
```

### 3. Запуск приложения

```bash
# Запуск Flask веб-приложения
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

# В отдельном терминале - запуск Telegram бота
python telegram_bot_service.py
```

Или используйте `main.py` который автоматически запустит оба сервиса:

```bash
python main.py
```

## Тестирование

### Запуск тестов

```bash
# Запуск всех тестов с покрытием
pytest --cov=. --cov-report=html --cov-report=term-missing

# Запуск отдельных тестовых модулей
pytest tests/test_home_assistant.py -v
pytest tests/test_bot.py -v
pytest tests/test_app.py -v
pytest tests/test_metrics.py -v

# Запуск асинхронных тестов
pytest tests/test_bot.py::TestTelegramBot::test_start_command -v
```

### Структура тестов

```
tests/
├── __init__.py              # Инициализация пакета тестов
├── conftest.py             # Фикстуры и конфигурация pytest
├── test_home_assistant.py  # Тесты Home Assistant API
├── test_bot.py            # Тесты Telegram бота
├── test_app.py            # Тесты Flask приложения
└── test_metrics.py        # Тесты системы метрик
```

### Покрытие кода

- Автоматическое измерение покрытия при каждом запуске тестов
- HTML отчет в папке `htmlcov/`
- XML отчет для интеграции с CI/CD
- Минимальное покрытие: 80%

### CI/CD Pipeline

- **GitHub Actions** для автоматического тестирования
- **Codecov** интеграция для отслеживания покрытия
- **Docker** тестирование сборки образа
- **Security scanning** для проверки уязвимостей
- **Code linting** с black, isort, flake8

## Архитектура

### Компоненты системы

- **Flask веб-приложение** (`app.py`) - Веб-интерфейс и API
- **Telegram бот** (`bot.py`) - Обработка команд Telegram
- **Home Assistant API** (`home_assistant.py`) - Клиент для работы с Home Assistant
- **Главный контроллер** (`main.py`) - Координация всех сервисов

### Структура проекта

```
├── app.py                    # Flask веб-приложение
├── bot.py                    # Telegram бот логика
├── bot_runner.py            # Автономный запуск бота
├── home_assistant.py        # Home Assistant API клиент
├── main.py                  # Главный контроллер приложения
├── telegram_bot_service.py  # Сервис Telegram бота
├── templates/
│   ├── base.html           # Базовый шаблон
│   └── index.html          # Главная страница
├── static/
│   └── style.css           # Стили интерфейса
├── pyproject.toml          # Зависимости Python
└── replit.md              # Документация проекта
```

## Настройка Home Assistant

### Создание токена доступа

1. Войдите в Home Assistant
2. Перейдите в Профиль → Токены долгосрочного доступа
3. Нажмите "Создать токен"
4. Скопируйте токен и установите как `HOME_ASSISTANT_TOKEN`

### Создание Telegram бота

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Выберите имя и username для бота
4. Скопируйте токен и установите как `TELEGRAM_BOT_TOKEN`

## Развертывание

### Replit (рекомендуется)

1. Форкните проект в Replit
2. Установите переменные окружения в Secrets
3. Запустите проект

### Локальное развертывание

```bash
git clone <your-repo-url>
cd home-assistant-telegram-bot
pip install -r requirements.txt
python main.py
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "main.py"]
```

## Мониторинг

Веб-интерфейс доступен по адресу `http://localhost:5000` и включает:

- Статистику устройств Home Assistant
- Статус сервисов в реальном времени
- Справку по командам Telegram бота
- Список активных световых устройств

## Безопасность

- Все соединения используют HTTPS/TLS
- Токены передаются через защищенные заголовки
- Сессии Flask защищены секретным ключом
- Telegram API использует официальную библиотеку с валидацией

## Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте логи в консоли приложения
2. Убедитесь, что все переменные окружения установлены корректно
3. Проверьте доступность Home Assistant по указанному URL
4. Убедитесь, что токен Home Assistant действителен

## Лицензия

MIT License - см. файл LICENSE для деталей.