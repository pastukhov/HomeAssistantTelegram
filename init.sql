-- Инициализация базы данных для Home Assistant Telegram Bot

-- Создаем пользователя и базу данных (если они не существуют)
CREATE DATABASE ha_telegram_bot;
CREATE USER ha_bot_user WITH ENCRYPTED PASSWORD 'secure_password_123';

-- Предоставляем права пользователю
GRANT ALL PRIVILEGES ON DATABASE ha_telegram_bot TO ha_bot_user;

-- Подключаемся к базе данных
\c ha_telegram_bot;

-- Создаем схему для логирования (опционально)
CREATE SCHEMA IF NOT EXISTS logs;

-- Таблица для хранения логов команд бота
CREATE TABLE IF NOT EXISTS logs.bot_commands (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username VARCHAR(100),
    command VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100),
    success BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица для хранения статистики использования
CREATE TABLE IF NOT EXISTS logs.usage_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    command_type VARCHAR(50) NOT NULL,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    UNIQUE(date, command_type)
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_bot_commands_user_id ON logs.bot_commands(user_id);
CREATE INDEX IF NOT EXISTS idx_bot_commands_created_at ON logs.bot_commands(created_at);
CREATE INDEX IF NOT EXISTS idx_usage_stats_date ON logs.usage_stats(date);

-- Предоставляем права на схему логирования
GRANT ALL PRIVILEGES ON SCHEMA logs TO ha_bot_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA logs TO ha_bot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA logs TO ha_bot_user;