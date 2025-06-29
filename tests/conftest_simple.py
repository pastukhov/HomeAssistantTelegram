"""
Simplified pytest configuration for Home Assistant Telegram Bot tests
"""
import pytest
import os
from unittest.mock import Mock, AsyncMock

# Set test environment variables
os.environ.update({
    'HOME_ASSISTANT_URL': 'http://test-ha.local:8123',
    'HOME_ASSISTANT_TOKEN': 'test_token_123',
    'TELEGRAM_BOT_TOKEN': 'test_bot_token_456',
    'SESSION_SECRET': 'test_secret_key'
})

@pytest.fixture
def mock_home_assistant():
    """Mock Home Assistant API client"""
    from home_assistant import HomeAssistantAPI
    
    mock_ha = Mock(spec=HomeAssistantAPI)
    mock_ha.test_connection.return_value = True
    mock_ha.get_all_states.return_value = [
        {"entity_id": "light.test", "state": "on", "attributes": {"friendly_name": "Test Light"}},
        {"entity_id": "switch.test", "state": "off", "attributes": {"friendly_name": "Test Switch"}}
    ]
    mock_ha.get_lights.return_value = [
        {"entity_id": "light.test", "state": "on", "attributes": {"friendly_name": "Test Light"}}
    ]
    
    return mock_ha

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
    mock_metrics.get_metrics_summary.return_value = {
        "app_uptime_seconds": 100,
        "memory_usage_mb": 50,
        "telegram_commands_total": 10,
        "ha_requests_total": 20
    }
    
    return mock_metrics