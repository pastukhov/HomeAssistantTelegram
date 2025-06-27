# Docker Deployment для Home Assistant Telegram Bot

## 🚀 Быстрый старт

### 1. Подготовка окружения

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd home-assistant-telegram-bot

# Создайте файл с переменными окружения
cp .env.example .env
```

### 2. Настройка переменных окружения

Отредактируйте файл `.env`:

```bash
# Database Configuration
DB_PASSWORD=your_secure_password_here

# Home Assistant Configuration
HOME_ASSISTANT_URL=https://your-home-assistant.domain.com
HOME_ASSISTANT_TOKEN=your_long_lived_access_token

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Flask Application Configuration
SESSION_SECRET=your_random_session_secret_key
```

### 3. Запуск приложения

#### Production (с базой данных и nginx)
```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f ha_telegram_bot
```

#### Development (без nginx, с live reload)
```bash
# Запуск в режиме разработки
docker-compose -f docker-compose.dev.yml up -d

# Просмотр логов
docker-compose -f docker-compose.dev.yml logs -f ha_telegram_bot_dev
```

#### Только основное приложение (без nginx)
```bash
# Запуск без reverse proxy
docker-compose up -d postgres ha_telegram_bot
```

## 📋 Компоненты системы

### Основные сервисы

1. **PostgreSQL Database** (`postgres`)
   - Порт: 5432 (production), 5433 (development)
   - База данных: `ha_telegram_bot`
   - Пользователь: `ha_bot_user`

2. **Home Assistant Telegram Bot** (`ha_telegram_bot`)
   - Порт: 5000 (production), 5001 (development)
   - Включает Flask веб-интерфейс и Telegram бота

3. **Nginx Reverse Proxy** (`nginx`) - опционально
   - Порт: 80 (HTTP), 443 (HTTPS)
   - SSL поддержка
   - Rate limiting
   - Security headers

## 🔧 Управление контейнерами

### Основные команды

```bash
# Запуск сервисов
docker-compose up -d

# Остановка сервисов
docker-compose down

# Перезапуск конкретного сервиса
docker-compose restart ha_telegram_bot

# Просмотр логов
docker-compose logs -f [service_name]

# Обновление образов
docker-compose pull
docker-compose up -d --force-recreate

# Полная очистка (ОСТОРОЖНО: удаляет данные!)
docker-compose down -v --remove-orphans
```

### Управление базой данных

```bash
# Подключение к базе данных
docker-compose exec postgres psql -U ha_bot_user -d ha_telegram_bot

# Резервное копирование
docker-compose exec postgres pg_dump -U ha_bot_user ha_telegram_bot > backup.sql

# Восстановление из резервной копии
docker-compose exec -T postgres psql -U ha_bot_user -d ha_telegram_bot < backup.sql
```

## 🔐 SSL Configuration (для nginx)

Создайте SSL сертификаты:

```bash
# Создайте директорию для SSL
mkdir ssl

# Самоподписанный сертификат (для тестирования)
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Или используйте Let's Encrypt
certbot certonly --standalone -d your-domain.com
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

Для запуска с nginx:
```bash
docker-compose --profile with-nginx up -d
```

## 🐛 Отладка и мониторинг

### Проверка состояния

```bash
# Проверка здоровья сервисов
docker-compose ps

# API статус
curl http://localhost:5000/api/status

# Логи конкретного сервиса
docker-compose logs -f ha_telegram_bot
```

### Распространенные проблемы

1. **База данных недоступна**
   ```bash
   # Проверьте статус postgres
   docker-compose logs postgres
   
   # Перезапустите базу данных
   docker-compose restart postgres
   ```

2. **Telegram бот не отвечает**
   ```bash
   # Проверьте переменные окружения
   docker-compose exec ha_telegram_bot env | grep TELEGRAM
   
   # Проверьте логи бота
   docker-compose logs -f ha_telegram_bot
   ```

3. **Home Assistant недоступен**
   ```bash
   # Проверьте URL и токен
   docker-compose exec ha_telegram_bot env | grep HOME_ASSISTANT
   
   # Тест подключения изнутри контейнера
   docker-compose exec ha_telegram_bot curl -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" $HOME_ASSISTANT_URL/api/
   ```

## 📊 Мониторинг

### Health Checks

Все сервисы имеют встроенные health checks:

- **PostgreSQL**: `pg_isready`
- **Application**: `curl /api/status`
- **Nginx**: автоматический

### Метрики

```bash
# Использование ресурсов
docker stats

# Размер образов
docker images

# Использование дисков
docker system df
```

## 🔄 Обновление

### Обновление приложения

```bash
# Получите последние изменения
git pull

# Пересоберите образ
docker-compose build ha_telegram_bot

# Перезапустите сервис
docker-compose up -d ha_telegram_bot
```

### Обновление зависимостей

```bash
# Обновите образы
docker-compose pull

# Пересоздайте контейнеры
docker-compose up -d --force-recreate
```

## 📝 Логирование

Логи сохраняются в:
- Контейнеры: `docker-compose logs`
- Приложение: `./logs/` директория (если настроена)
- База данных: таблица `logs.bot_commands`

### Настройка ротации логов

```bash
# Добавьте в docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🔒 Безопасность

### Рекомендации

1. **Измените пароли по умолчанию**
2. **Используйте сильные секретные ключи**
3. **Настройте брандмауэр**
4. **Обновляйте образы регулярно**
5. **Используйте HTTPS в production**

### Сетевая безопасность

```bash
# Ограничьте доступ к базе данных
# В docker-compose.yml уберите порт postgres из публичного доступа
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs -f`
2. Убедитесь в правильности переменных окружения
3. Проверьте сетевое подключение к Home Assistant
4. Проверьте статус Telegram Bot API