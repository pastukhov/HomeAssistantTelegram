# Инструкция по загрузке проекта на GitHub

## Подготовка к загрузке

Ваш проект готов к загрузке на GitHub. Все необходимые файлы созданы:

- ✅ `.gitignore` - исключает временные и системные файлы
- ✅ `README.md` - полная документация проекта
- ✅ Весь исходный код приложения

## Шаги для загрузки на GitHub

### 1. Создание приватного репозитория

1. Войдите в GitHub.com
2. Нажмите "New repository" (зеленая кнопка)
3. Заполните поля:
   - **Repository name**: `home-assistant-telegram-bot`
   - **Description**: `Home Assistant Telegram Bot с веб-интерфейсом`
   - ✅ **Private** (выберите приватный репозиторий)
   - ✅ **Add README file** (снимите галочку, у нас уже есть README)
4. Нажмите "Create repository"

### 2. Загрузка кода через веб-интерфейс GitHub

#### Способ 1: Загрузка файлов через веб-интерфейс (рекомендуется)

1. На странице созданного репозитория нажмите "uploading an existing file"
2. Перетащите все файлы проекта или выберите их:
   - `app.py`
   - `bot.py` 
   - `bot_runner.py`
   - `home_assistant.py`
   - `main.py`
   - `telegram_bot_service.py`
   - `pyproject.toml`
   - `uv.lock`
   - `replit.md`
   - `README.md`
   - `.gitignore`
   - `GITHUB_SETUP.md`
   - Папку `templates/` с файлами
   - Папку `static/` с файлами
3. Добавьте commit message: "Initial commit: Home Assistant Telegram Bot"
4. Нажмите "Commit changes"

#### Способ 2: Через Git командную строку (если у вас установлен Git)

```bash
# В терминале Replit выполните:
git init
git add .
git commit -m "Initial commit: Home Assistant Telegram Bot"
git branch -M main
git remote add origin https://github.com/ВАШЕ_ИМЯ/home-assistant-telegram-bot.git
git push -u origin main
```

### 3. Скачивание кода из Replit

Если вы хотите сначала скачать код локально:

1. В Replit нажмите на меню (три точки) рядом с "Files"
2. Выберите "Download as zip"
3. Распакуйте архив на своем компьютере
4. Загрузите файлы на GitHub через веб-интерфейс

## Что НЕ загружать на GitHub

Файлы в `.gitignore` автоматически исключены:
- `__pycache__/` - кэш Python
- `*.log` - файлы логов
- `*.pid` - файлы процессов  
- `.env` - переменные окружения (ВАЖНО: не загружайте секреты!)
- `.replit` - конфигурация Replit

## Настройка переменных окружения на новом сервере

После клонирования репозитория создайте файл `.env`:

```env
HOME_ASSISTANT_URL=https://ваш-home-assistant-url
HOME_ASSISTANT_TOKEN=ваш_токен_home_assistant
TELEGRAM_BOT_TOKEN=ваш_токен_telegram_бота
SESSION_SECRET=ваш_секретный_ключ_flask
```

## Готово!

После загрузки у вас будет приватный репозиторий с полным кодом проекта, который можно:

- Клонировать на другие серверы
- Развернуть в облачных сервисах
- Поделиться с командой (добавив коллабораторов)
- Отслеживать изменения через Git

Ваш Telegram бот будет доступен в любом месте, где вы развернете этот код!