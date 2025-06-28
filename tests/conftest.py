"""
Pytest configuration and fixtures for Home Assistant Telegram Bot tests
"""
import pytest
import os
from unittest.mock import Mock, AsyncMock

# Try importing from python-telegram-bot v20+
try:
    from telegram import Update, User, Chat, Message
    from telegram.ext import ContextTypes
except ImportError:
    # Fallback for older versions or missing components
    Update = Mock
    User = Mock
    Chat = Mock
    Message = Mock
    
    class MockContextTypes:
        DEFAULT_TYPE = Mock
    
    ContextTypes = MockContextTypes()


@pytest.fixture
def mock_home_assistant():
    """Mock Home Assistant API client"""
    from home_assistant import HomeAssistantAPI
    
    mock_ha = Mock(spec=HomeAssistantAPI)
    mock_ha.test_connection.return_value = True
    mock_ha.get_all_states.return_value = [
        {
            "entity_id": "light.test_light",
            "state": "off",
            "attributes": {"friendly_name": "Test Light"},
        },
        {
            "entity_id": "switch.test_switch", 
            "state": "on",
            "attributes": {"friendly_name": "Test Switch"},
        }
    ]
    mock_ha.get_lights.return_value = [
        {
            "entity_id": "light.test_light",
            "state": "off",
            "attributes": {"friendly_name": "Test Light"},
        }
    ]
    mock_ha.get_switches.return_value = [
        {
            "entity_id": "switch.test_switch",
            "state": "on", 
            "attributes": {"friendly_name": "Test Switch"},
        }
    ]
    mock_ha.get_sensors.return_value = [
        {
            "entity_id": "sensor.test_temperature",
            "state": "22.5",
            "attributes": {"friendly_name": "Test Temperature", "unit_of_measurement": "°C"},
        }
    ]
    mock_ha.turn_on_light.return_value = True
    mock_ha.turn_off_light.return_value = True
    mock_ha.turn_on_switch.return_value = True
    mock_ha.turn_off_switch.return_value = True
    
    return mock_ha


@pytest.fixture
def mock_update():
    """Mock Telegram Update object"""
    update = Mock(spec=Update)
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 123456789
    update.effective_user.first_name = "Test"
    update.effective_user.username = "testuser"
    
    update.effective_chat = Mock(spec=Chat)
    update.effective_chat.id = 123456789
    update.effective_chat.type = "private"
    
    update.message = Mock(spec=Message)
    update.message.reply_text = AsyncMock()
    update.message.text = "/test"
    update.message.chat = update.effective_chat
    update.message.from_user = update.effective_user
    
    return update


@pytest.fixture
def mock_context():
    """Mock Telegram Context object"""
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = []
    context.bot = AsyncMock()
    return context


@pytest.fixture
def flask_app():
    """Flask application test client"""
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_metrics():
    """Mock metrics collector"""
    from metrics import MetricsCollector
    
    mock_metrics = Mock(spec=MetricsCollector)
    mock_metrics.record_telegram_command = Mock()
    mock_metrics.record_homeassistant_request = Mock() 
    mock_metrics.record_device_command = Mock()
    mock_metrics.update_device_status = Mock()
    mock_metrics.get_metrics_summary.return_value = {
        "app_uptime_seconds": 100,
        "memory_usage_mb": 50,
        "total_commands": 10,
        "successful_commands": 9,
        "failed_commands": 1,
        "active_users": 1,
        "homeassistant_entities": {"light": 5, "switch": 3, "sensor": 10}
    }
    
    return mock_metrics


@pytest.fixture(autouse=True)
def mock_environment():
    """Mock environment variables"""
    test_env = {
        'HOME_ASSISTANT_URL': 'http://test-ha.local:8123',
        'HOME_ASSISTANT_TOKEN': 'test_token_123',
        'TELEGRAM_BOT_TOKEN': 'test_bot_token_456',
        'SESSION_SECRET': 'test_secret_key'
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    yield test_env
    
    # Cleanup
    for key in test_env.keys():
        if key in os.environ:
            del os.environ[key]