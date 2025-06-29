"""
OpenMetrics система для Home Assistant Telegram Bot
Собирает метрики производительности и использования
"""

import functools
import logging
import time
from typing import Any
from typing import Dict
from typing import Optional

from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import Info
from prometheus_client import generate_latest
from prometheus_client import start_http_server
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

# === TELEGRAM BOT МЕТРИКИ ===

# Счетчики команд
telegram_commands_total = Counter(
    "telegram_bot_commands_total",
    "Общее количество выполненных команд Telegram бота",
    ["command", "user_id", "status"],
)

# Время выполнения команд
telegram_command_duration = Histogram(
    "telegram_bot_command_duration_seconds",
    "Время выполнения команд Telegram бота",
    ["command"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

# Активные пользователи
telegram_active_users = Gauge(
    "telegram_bot_active_users",
    "Количество активных пользователей за последние 24 часа",
)

# === HOME ASSISTANT API МЕТРИКИ ===

# Запросы к Home Assistant API
homeassistant_api_requests_total = Counter(
    "homeassistant_api_requests_total",
    "Общее количество запросов к Home Assistant API",
    ["method", "endpoint", "status_code"],
)

# Время ответа Home Assistant API
homeassistant_api_duration = Histogram(
    "homeassistant_api_duration_seconds",
    "Время ответа Home Assistant API",
    ["method", "endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

# Состояние подключения к Home Assistant
homeassistant_connection_status = Gauge(
    "homeassistant_connection_status",
    "Статус подключения к Home Assistant (1=подключен, 0=отключен)",
)

# Количество сущностей в Home Assistant
homeassistant_entities_total = Gauge(
    "homeassistant_entities_total",
    "Общее количество сущностей в Home Assistant",
    ["domain"],
)

# === СИСТЕМНЫЕ МЕТРИКИ ===

# Информация о приложении
app_info = Info("app_info", "Информация о приложении")

# Время работы приложения
app_uptime_seconds = Gauge("app_uptime_seconds", "Время работы приложения в секундах")

# Использование памяти
app_memory_usage_bytes = Gauge(
    "app_memory_usage_bytes", "Использование памяти приложением в байтах"
)

# === МЕТРИКИ УСТРОЙСТВ ===

# Команды управления устройствами
device_commands_total = Counter(
    "device_commands_total",
    "Количество команд управления устройствами",
    ["entity_id", "command", "success"],
)

# Время выполнения команд устройств
device_command_duration = Histogram(
    "device_command_duration_seconds",
    "Время выполнения команд управления устройствами",
    ["entity_id", "command"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

# Состояние устройств
device_status = Gauge(
    "device_status",
    "Текущее состояние устройств (1=on, 0=off, -1=unavailable)",
    ["entity_id", "friendly_name"],
)


class MetricsCollector:
    """Класс для сбора и управления метриками"""

    def __init__(self):
        self.start_time = time.time()
        self.active_users_cache = set()
        self.last_cleanup = time.time()

        # Инициализация базовой информации о приложении
        app_info.info(
            {
                "version": "1.0.0",
                "python_version": self._get_python_version(),
                "start_time": str(int(self.start_time)),
            }
        )

    def _get_python_version(self) -> str:
        """Получить версию Python"""
        import sys

        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def update_app_uptime(self):
        """Обновить метрику времени работы приложения"""
        uptime = time.time() - self.start_time
        app_uptime_seconds.set(uptime)

    def update_memory_usage(self):
        """Обновить метрику использования памяти"""
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss
            app_memory_usage_bytes.set(memory_usage)
        except ImportError:
            # psutil не установлен, пропускаем
            pass
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")

    def record_telegram_command(
        self, command: str, user_id: str, success: bool, duration: float
    ):
        """Записать метрики команды Telegram бота"""
        status = "success" if success else "error"

        # Увеличиваем счетчик команд
        telegram_commands_total.labels(
            command=command, user_id=user_id, status=status
        ).inc()

        # Записываем время выполнения
        telegram_command_duration.labels(command=command).observe(duration)

        # Добавляем пользователя в активные
        self.active_users_cache.add(user_id)
        self._cleanup_active_users()

    def record_homeassistant_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Записать метрики запроса к Home Assistant API"""
        # Увеличиваем счетчик запросов
        homeassistant_api_requests_total.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        # Записываем время ответа
        homeassistant_api_duration.labels(method=method, endpoint=endpoint).observe(
            duration
        )

        # Обновляем статус подключения
        connection_status = 1 if status_code == 200 else 0
        homeassistant_connection_status.set(connection_status)

    def record_device_command(
        self, entity_id: str, command: str, success: bool, duration: float
    ):
        """Записать метрики команды управления устройством"""
        # Увеличиваем счетчик команд устройств
        device_commands_total.labels(
            entity_id=entity_id, command=command, success=str(success).lower()
        ).inc()

        # Записываем время выполнения
        device_command_duration.labels(entity_id=entity_id, command=command).observe(
            duration
        )

    def update_device_status(self, entity_id: str, friendly_name: str, state: str):
        """Обновить статус устройства"""
        # Преобразуем состояние в числовое значение
        if state == "on":
            status_value = 1
        elif state == "off":
            status_value = 0
        elif state == "unavailable":
            status_value = -1
        else:
            status_value = 0

        device_status.labels(entity_id=entity_id, friendly_name=friendly_name).set(
            status_value
        )

    def update_homeassistant_entities(self, entities_by_domain: Dict[str, int]):
        """Обновить количество сущностей по доменам"""
        for domain, count in entities_by_domain.items():
            homeassistant_entities_total.labels(domain=domain).set(count)

    def _cleanup_active_users(self):
        """Очистка кэша активных пользователей (каждые 24 часа)"""
        current_time = time.time()
        if current_time - self.last_cleanup > 86400:  # 24 часа
            self.active_users_cache.clear()
            self.last_cleanup = current_time

        # Обновляем метрику активных пользователей
        telegram_active_users.set(len(self.active_users_cache))

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Получить сводку всех метрик"""
        return {
            "uptime_seconds": time.time() - self.start_time,
            "active_users": len(self.active_users_cache),
            "total_commands": sum(
                [
                    metric.labels(command=cmd, user_id=uid, status=status)._value.get()
                    for metric in [telegram_commands_total]
                    for cmd in [
                        "start",
                        "help",
                        "status",
                        "lights",
                        "switches",
                        "sensors",
                    ]
                    for uid in ["all"]
                    for status in ["success", "error"]
                ]
            ),
            "homeassistant_connection": homeassistant_connection_status._value.get(),
        }


# Глобальный экземпляр коллектора метрик
metrics_collector = MetricsCollector()


def track_telegram_command(command_name: str):
    """Декоратор для отслеживания команд Telegram бота"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            start_time = time.time()
            user_id = (
                str(update.effective_user.id) if update.effective_user else "unknown"
            )
            success = False

            try:
                result = await func(update, context, *args, **kwargs)
                success = True
                return result
            except Exception as e:
                logger.error(f"Error in command {command_name}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_telegram_command(
                    command=command_name,
                    user_id=user_id,
                    success=success,
                    duration=duration,
                )

        return wrapper

    return decorator


def track_homeassistant_request(method: str, endpoint: str):
    """Декоратор для отслеживания запросов к Home Assistant API"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 0

            try:
                result = func(*args, **kwargs)
                status_code = 200 if result is not None else 500
                return result
            except Exception as e:
                status_code = 500
                logger.error(
                    f"Error in Home Assistant request {method} {endpoint}: {e}"
                )
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_homeassistant_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code,
                    duration=duration,
                )

        return wrapper

    return decorator


def track_device_command(entity_id: str, command: str):
    """Декоратор для отслеживания команд управления устройствами"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False

            try:
                result = func(*args, **kwargs)
                success = bool(result)
                return result
            except Exception as e:
                logger.error(f"Error in device command {command} for {entity_id}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_device_command(
                    entity_id=entity_id,
                    command=command,
                    success=success,
                    duration=duration,
                )

        return wrapper

    return decorator


def start_metrics_server(port: int = 8000):
    """Запустить HTTP сервер для метрик"""
    try:
        start_http_server(port)
        logger.info(f"Metrics server started on port {port}")
        logger.info(f"Metrics available at http://localhost:{port}/metrics")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")


def update_system_metrics():
    """Обновить системные метрики"""
    metrics_collector.update_app_uptime()
    metrics_collector.update_memory_usage()
