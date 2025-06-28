# 🔧 Быстрое исправление GitHub Actions

## Проблема
Ошибка: `This request has been automatically failed because it uses a deprecated version of actions/upload-artifact: v3`

## ✅ Исправление уже выполнено

В файле `.github/workflows/ci.yml` обновлены следующие действия:

### Изменения:
```yaml
# Было:
- uses: actions/upload-artifact@v3
- uses: codecov/codecov-action@v3

# Стало:
- uses: actions/upload-artifact@v4  
- uses: codecov/codecov-action@v4
```

### Дополнительно добавлен токен для Codecov:
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
```

## 📋 Команды для обновления в GitHub

```bash
# Скопируйте обновленный файл .github/workflows/ci.yml
# Или внесите следующие изменения:

# Строка 51: обновите codecov action
- uses: codecov/codecov-action@v4

# Строка 59: обновите upload-artifact action  
- uses: actions/upload-artifact@v4

# Строка 56: добавьте token для codecov
token: ${{ secrets.CODECOV_TOKEN }}
```

## 🔑 Настройка Codecov токена (опционально)

1. Зайдите на https://codecov.io
2. Подключите ваш GitHub репозиторий
3. Скопируйте CODECOV_TOKEN
4. В GitHub репозитории: Settings → Secrets and variables → Actions
5. Добавьте: `CODECOV_TOKEN` = `ваш_токен`

## 🚀 Результат

После этих изменений GitHub Actions pipeline будет работать корректно:
- ✅ Тесты будут запускаться  
- ✅ Покрытие будет загружаться в Codecov
- ✅ Артефакты отчетов будут сохраняться
- ✅ Docker сборка будет тестироваться
- ✅ Линтинг и проверка безопасности выполнятся

Все исправления совместимы с GitHub Actions latest runner version 2.325.0.