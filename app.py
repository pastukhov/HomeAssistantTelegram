import logging
import os

from flask import Flask
from flask import Response
from flask import jsonify
from flask import render_template
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import generate_latest

from home_assistant import HomeAssistantAPI
from metrics import metrics_collector
from metrics import start_metrics_server
from metrics import update_system_metrics

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key")

# Initialize Home Assistant API
ha_api = HomeAssistantAPI()

# Запуск сервера метрик
try:
    start_metrics_server(port=8000)
except Exception as e:
    logger.warning(f"Could not start metrics server: {e}")


@app.route("/")
def index():
    """Main dashboard page"""
    try:
        # Get basic system info
        states = ha_api.get_all_states()
        system_info = {
            "total_entities": len(states) if states else 0,
            "lights": (
                len([s for s in states if s.get("entity_id", "").startswith("light.")])
                if states
                else 0
            ),
            "switches": (
                len([s for s in states if s.get("entity_id", "").startswith("switch.")])
                if states
                else 0
            ),
            "sensors": (
                len([s for s in states if s.get("entity_id", "").startswith("sensor.")])
                if states
                else 0
            ),
        }

        # Get recent light states
        recent_lights = []
        if states:
            lights = [s for s in states if s.get("entity_id", "").startswith("light.")][
                :10
            ]
            for light in lights:
                recent_lights.append(
                    {
                        "entity_id": light.get("entity_id", "Unknown"),
                        "state": light.get("state", "Unknown"),
                        "friendly_name": light.get("attributes", {}).get(
                            "friendly_name", light.get("entity_id", "Unknown")
                        ),
                    }
                )

        return render_template(
            "index.html",
            system_info=system_info,
            recent_lights=recent_lights,
            ha_connected=True,
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template(
            "index.html",
            system_info={"total_entities": 0, "lights": 0, "switches": 0, "sensors": 0},
            recent_lights=[],
            ha_connected=False,
            error=str(e),
        )


@app.route("/api/status")
def api_status():
    """API endpoint for bot status"""
    try:
        states = ha_api.get_all_states()

        # Check Telegram bot status
        telegram_status = "disabled"
        try:
            with open("telegram_bot.pid", "r") as f:
                pid = int(f.read().strip())
                # Check if process is running
                import os

                try:
                    os.kill(pid, 0)
                    telegram_status = "running"
                except OSError:
                    telegram_status = "stopped"
        except FileNotFoundError:
            telegram_status = "not_started"
        except Exception:
            telegram_status = "unknown"

        return jsonify(
            {
                "status": "connected",
                "entities_count": len(states) if states else 0,
                "telegram_bot": telegram_status,
                "timestamp": ha_api.get_current_time(),
            }
        )
    except Exception as e:
        logger.error(f"API status error: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "telegram_bot": "error",
                    "timestamp": None,
                }
            ),
            500,
        )


@app.route("/api/lights")
def api_lights():
    """API endpoint for lights status"""
    try:
        lights = ha_api.get_lights()
        return jsonify({"status": "success", "lights": lights})
    except Exception as e:
        logger.error(f"API lights error: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/metrics")
def metrics():
    """OpenMetrics endpoint for Prometheus scraping"""
    try:
        # Обновляем системные метрики перед отдачей
        update_system_metrics()

        # Обновляем метрики Home Assistant
        _update_homeassistant_metrics()

        # Генерируем метрики в формате OpenMetrics
        data = generate_latest()
        return Response(data, mimetype=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        return Response("# Metrics unavailable\n", mimetype="text/plain"), 500


@app.route("/api/metrics-summary")
def api_metrics_summary():
    """API endpoint for metrics summary"""
    try:
        summary = metrics_collector.get_metrics_summary()
        return jsonify({"status": "success", "metrics": summary})
    except Exception as e:
        logger.error(f"Metrics summary error: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


def _update_homeassistant_metrics():
    """Обновить метрики Home Assistant"""
    try:
        # Получаем все состояния
        states = ha_api.get_all_states()
        if states:
            # Подсчитываем сущности по доменам
            entities_by_domain = {}
            for state in states:
                entity_id = state.get("entity_id", "")
                if "." in entity_id:
                    domain = entity_id.split(".")[0]
                    entities_by_domain[domain] = entities_by_domain.get(domain, 0) + 1

                    # Обновляем статус устройств для основных доменов
                    if domain in ["light", "switch", "sensor"]:
                        friendly_name = state.get("attributes", {}).get(
                            "friendly_name", entity_id
                        )
                        current_state = state.get("state", "unknown")
                        metrics_collector.update_device_status(
                            entity_id, friendly_name, current_state
                        )

            # Обновляем метрики количества сущностей
            metrics_collector.update_homeassistant_entities(entities_by_domain)

            # Устанавливаем статус подключения
            from metrics import homeassistant_connection_status

            homeassistant_connection_status.set(1)
        else:
            # Нет данных - проблемы с подключением
            from metrics import homeassistant_connection_status

            homeassistant_connection_status.set(0)

    except Exception as e:
        logger.error(f"Error updating Home Assistant metrics: {e}")
        from metrics import homeassistant_connection_status

        homeassistant_connection_status.set(0)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
