# Docker Deployment Guide

Упрощенное руководство по развертыванию Home Assistant Telegram Bot с Docker.

## Быстрый старт

### 1. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
HOME_ASSISTANT_URL=https://your-homeassistant-url.com
HOME_ASSISTANT_TOKEN=your_long_lived_access_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SESSION_SECRET=your_random_secret_key_here
```

### 2. Запуск в production режиме

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 3. Запуск в development режиме

```bash
# Запуск с live reload
docker-compose -f docker-compose.dev.yml up

# В фоновом режиме
docker-compose -f docker-compose.dev.yml up -d
```

## Доступные эндпоинты

После запуска приложение будет доступно:

- **Веб-интерфейс**: http://localhost:5000
- **API статуса**: http://localhost:5000/api/status
- **Метрики**: http://localhost:5000/metrics
- **Сводка метрик**: http://localhost:5000/api/metrics-summary

## Конфигурация

### Production окружение

```yaml
# docker-compose.yml
services:
  ha_telegram_bot:
    build: .
    ports:
      - "5000:5000"
      - "8000:8000"  # Порт метрик
    environment:
      - HOME_ASSISTANT_URL=${HOME_ASSISTANT_URL}
      - HOME_ASSISTANT_TOKEN=${HOME_ASSISTANT_TOKEN}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - SESSION_SECRET=${SESSION_SECRET}
```

### Development окружение

```yaml
# docker-compose.dev.yml
services:
  ha_telegram_bot_dev:
    volumes:
      - .:/app  # Live reload
    command: ["python", "main.py"]
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
```

## Мониторинг

### Health Checks

Docker включает встроенные проверки здоровья:

```bash
# Проверка статуса контейнера
docker-compose ps

# Просмотр результатов health check
docker inspect ha_telegram_bot_app | grep -A 10 Health
```

### Логи

```bash
# Все логи
docker-compose logs

# Логи в реальном времени
docker-compose logs -f

# Логи только приложения
docker-compose logs ha_telegram_bot
```

### Метрики

Система включает OpenMetrics для мониторинга:

- **Prometheus**: http://localhost:5000/metrics
- **Веб-дашборд**: http://localhost:5000 (секция "System Metrics")

## Развертывание в продакшне

### С reverse proxy (Nginx/Traefik)

```yaml
# Добавьте в docker-compose.yml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.ha-bot.rule=Host(`your-domain.com`)"
  - "traefik.http.routers.ha-bot.tls=true"
```

### Безопасность

1. **Используйте сильные пароли** для SESSION_SECRET
2. **Ограничьте доступ** к портам 5000 и 8000
3. **Используйте HTTPS** для внешнего доступа
4. **Регулярно обновляйте** токены Home Assistant

### Backup

```bash
# Сохранение логов
docker cp ha_telegram_bot_app:/app/logs ./backup/logs/

# Экспорт конфигурации
cp .env ./backup/
cp docker-compose.yml ./backup/
```

## Устранение неполадок

### Проблемы с подключением

```bash
# Проверка сети
docker-compose exec ha_telegram_bot ping home-assistant-host

# Проверка переменных окружения
docker-compose exec ha_telegram_bot env | grep HOME_ASSISTANT
```

### Проблемы с Telegram ботом

```bash
# Проверка токена
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"

# Логи бота
docker-compose logs ha_telegram_bot | grep telegram
```

### Перезапуск сервисов

```bash
# Перезапуск без пересборки
docker-compose restart

# Полная пересборка
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Обновление

```bash
# Получение обновлений
git pull origin main

# Пересборка с новыми изменениями
docker-compose down
docker-compose build
docker-compose up -d
```