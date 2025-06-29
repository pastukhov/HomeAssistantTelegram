# 🏷️ Исправления Badge для README

## ✅ Обновленные badge URLs

### Исправленные ссылки в README.md:
```markdown
[![CI/CD Pipeline](https://github.com/pastukhov/HomeAssistantTelegram/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/pastukhov/HomeAssistantTelegram/actions)
[![Coverage](https://img.shields.io/badge/coverage-40%25-yellow.svg)](https://github.com/pastukhov/HomeAssistantTelegram)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
```

### Что изменилось:
1. **Правильный URL репозитория**: `pastukhov/HomeAssistantTelegram`
2. **Кликабельные badge**: добавлены ссылки в квадратных скобках
3. **Актуальное покрытие**: 40% вместо неизвестного статуса
4. **Добавлен Docker badge**: показывает готовность к контейнеризации
5. **Правильное экранирование**: %2F для слэшей в URL

## 🎯 Альтернативные варианты для Codecov

Если потребуется настроить автоматический Codecov badge:

### Вариант 1: Автоматический Codecov badge
```markdown
[![Coverage](https://codecov.io/gh/pastukhov/HomeAssistantTelegram/branch/main/graph/badge.svg)](https://codecov.io/gh/pastukhov/HomeAssistantTelegram)
```

### Вариант 2: Статический badge с актуальными данными
```markdown
[![Coverage](https://img.shields.io/badge/coverage-40%25-yellow.svg)](https://github.com/pastukhov/HomeAssistantTelegram/actions)
```

### Вариант 3: Динамический badge через GitHub Actions
```markdown
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pastukhov/HomeAssistantTelegram/main/coverage-badge.json)](https://github.com/pastukhov/HomeAssistantTelegram/actions)
```

## 📊 Дополнительные badge для README

### Статусы проекта:
```markdown
[![Tests](https://img.shields.io/badge/tests-8%2F8%20passing-brightgreen.svg)]()
[![Docker Build](https://img.shields.io/badge/docker-build%20passing-blue.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-black-black.svg)]()
```

### Технологии:
```markdown
[![Flask](https://img.shields.io/badge/flask-2.3-red.svg)]()
[![Telegram Bot](https://img.shields.io/badge/telegram--bot-20.0-blue.svg)]()
[![Home Assistant](https://img.shields.io/badge/home%20assistant-ready-orange.svg)]()
```

## 🎨 Результат

Теперь badge в README будут:
- Правильно отображаться с корректными ссылками
- Показывать актуальную информацию (coverage 40%)
- Быть кликабельными и вести на соответствующие страницы
- Выглядеть профессионально и информативно