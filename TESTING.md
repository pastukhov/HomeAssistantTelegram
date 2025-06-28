# Testing Guide

Комплексное руководство по тестированию Home Assistant Telegram Bot.

## Быстрый старт

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=. --cov-report=html --cov-report=term-missing

# Запуск отдельного модуля тестов
pytest tests/test_basic.py -v

# Запуск конкретного теста
pytest tests/test_basic.py::TestBasicFunctionality::test_imports -v
```

## Структура тестов

### Базовые тесты (`test_basic.py`)
- ✅ Тестирование импортов модулей
- ✅ Проверка переменных окружения
- ✅ Инициализация компонентов
- ✅ Существование файлов и функций

**Статус**: Все тесты проходят (8/8)

### Тесты Home Assistant API (`test_home_assistant.py`)
- ⚠️ Тестирование HTTP-запросов к API
- ⚠️ Обработка ошибок соединения
- ✅ Фильтрация устройств по типу
- ✅ Управление освещением и выключателями

**Статус**: Частично работают (требуют улучшения мокинга)

### Тесты Telegram бота (`test_bot.py`)
- ⚠️ Асинхронные команды бота
- ⚠️ Обработка пользовательского ввода
- ⚠️ Интеграция с Home Assistant API

**Статус**: Требуют исправления импортов telegram-bot

### Тесты Flask приложения (`test_app.py`)
- ✅ HTTP роуты и ответы
- ⚠️ API эндпоинты
- ⚠️ Интеграция с метриками

**Статус**: Основные роуты работают

### Тесты системы метрик (`test_metrics.py`)
- ✅ Инициализация MetricsCollector
- ✅ Запись метрик производительности
- ⚠️ Декораторы отслеживания

**Статус**: Базовые функции работают

## Покрытие кода

**Текущее покрытие**: 55%

### По модулям:
- `metrics.py`: 82% (отличное покрытие)
- `app.py`: 54% (требует расширения тестов)
- `home_assistant.py`: 31% (требует мокинга HTTP)

## Конфигурация

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
addopts = --verbose --cov=. --cov-report=html:htmlcov --cov-report=xml:coverage.xml
asyncio_mode = auto
```

### Переменные окружения для тестов
```bash
HOME_ASSISTANT_URL=http://test-ha.local:8123
HOME_ASSISTANT_TOKEN=test_token_123
TELEGRAM_BOT_TOKEN=test_bot_token_456
SESSION_SECRET=test_secret_key
```

## Фикстуры (conftest.py)

### Доступные фикстуры:
- `mock_home_assistant`: Мок Home Assistant API
- `mock_update`: Мок Telegram Update объекта
- `mock_context`: Мок Telegram Context
- `flask_app`: Flask test client
- `mock_metrics`: Мок системы метрик
- `mock_environment`: Автоматическое мокирование переменных окружения

## Запуск в CI/CD

### GitHub Actions
```yaml
# .github/workflows/ci.yml
- name: Run tests with coverage
  run: pytest --cov=. --cov-report=xml --verbose

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
```

### Docker тестирование
```bash
# Сборка тестового образа
docker build -t ha-telegram-bot:test .

# Запуск тестов в контейнере
docker run --rm ha-telegram-bot:test pytest
```

## Troubleshooting

### Проблема с импортами telegram
**Ошибка**: `ImportError: cannot import name 'Update' from 'telegram'`

**Решение**: Тесты для telegram-bot компонентов временно отключены из-за конфликтов версий библиотеки.

### Проблема с HTTP соединениями
**Ошибка**: `ConnectionError: Failed to resolve 'test-ha.local'`

**Решение**: Используйте мокинг для изоляции тестов от внешних зависимостей.

### Проблема с async тестами
**Ошибка**: `RuntimeError: There is no current event loop`

**Решение**: Убедитесь что используете `@pytest.mark.asyncio` для асинхронных тестов.

## Расширение тестов

### Добавление нового теста
```python
def test_new_functionality(self):
    """Test description"""
    # Arrange
    expected_result = "test_value"
    
    # Act
    result = function_to_test()
    
    # Assert
    assert result == expected_result
```

### Мокирование внешних зависимостей
```python
@patch('module.external_service')
def test_with_mock(self, mock_service):
    mock_service.return_value = "mocked_response"
    # Test logic here
```

## Цели улучшения

### Ближайшие задачи:
1. ✅ Базовое тестирование всех модулей
2. 🔄 Исправление импортов telegram-bot библиотеки
3. 🔄 Улучшение мокирования HTTP запросов
4. 📋 Увеличение покрытия до 80%
5. 📋 Добавление интеграционных тестов

### Долгосрочные цели:
- Автоматическое тестирование при каждом коммите
- Интеграция с системой уведомлений о падении тестов
- Performance тестирование для метрик
- E2E тестирование через Docker Compose

## Заключение

Система тестирования успешно настроена и функционирует. Базовые тесты проходят, система покрытия работает, CI/CD pipeline готов к использованию.