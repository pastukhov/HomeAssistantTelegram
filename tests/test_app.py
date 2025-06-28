"""
Tests for Flask web application
"""
import pytest
import json
from unittest.mock import patch, Mock


class TestFlaskApp:
    """Test cases for Flask web application"""
    
    def test_index_route(self, flask_app):
        """Test main dashboard page"""
        response = flask_app.get('/')
        assert response.status_code == 200
        assert b'Home Assistant Telegram Bot' in response.data
        assert b'System Status' in response.data
    
    @patch('app.ha_client')
    def test_api_status_success(self, mock_ha_client, flask_app):
        """Test /api/status endpoint with successful connection"""
        mock_ha_client.test_connection.return_value = True
        mock_ha_client.get_all_states.return_value = [
            {"entity_id": "light.test", "state": "on"},
            {"entity_id": "switch.test", "state": "off"}
        ]
        
        response = flask_app.get('/api/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['home_assistant']['connected'] is True
        assert data['telegram_bot']['running'] is True
        assert data['total_entities'] == 2
    
    @patch('app.ha_client')
    def test_api_status_failure(self, mock_ha_client, flask_app):
        """Test /api/status endpoint with connection failure"""
        mock_ha_client.test_connection.return_value = False
        mock_ha_client.get_all_states.return_value = None
        
        response = flask_app.get('/api/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['home_assistant']['connected'] is False
        assert data['total_entities'] == 0
    
    @patch('app.ha_client')
    def test_api_lights(self, mock_ha_client, flask_app):
        """Test /api/lights endpoint"""
        mock_ha_client.get_lights.return_value = [
            {
                "entity_id": "light.bedroom",
                "state": "on", 
                "attributes": {"friendly_name": "Bedroom Light"}
            },
            {
                "entity_id": "light.kitchen",
                "state": "off",
                "attributes": {"friendly_name": "Kitchen Light"}
            }
        ]
        
        response = flask_app.get('/api/lights')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['entity_id'] == 'light.bedroom'
        assert data[0]['state'] == 'on'
        assert data[1]['state'] == 'off'
    
    @patch('app.ha_client')
    def test_api_lights_error(self, mock_ha_client, flask_app):
        """Test /api/lights endpoint with error"""
        mock_ha_client.get_lights.side_effect = Exception("API Error")
        
        response = flask_app.get('/api/lights')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_metrics_endpoint(self, flask_app):
        """Test /metrics endpoint for Prometheus"""
        response = flask_app.get('/metrics')
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain')
        
        # Check for basic metrics
        assert b'app_uptime_seconds' in response.data
        assert b'app_memory_usage_bytes' in response.data
    
    @patch('app.metrics_collector')
    def test_api_metrics_summary(self, mock_metrics, flask_app):
        """Test /api/metrics-summary endpoint"""
        mock_metrics.get_metrics_summary.return_value = {
            "app_uptime_seconds": 100,
            "memory_usage_mb": 50,
            "total_commands": 10,
            "successful_commands": 9,
            "failed_commands": 1,
            "active_users": 1,
            "homeassistant_entities": {"light": 5, "switch": 3}
        }
        
        response = flask_app.get('/api/metrics-summary')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['app_uptime_seconds'] == 100
        assert data['memory_usage_mb'] == 50
        assert data['total_commands'] == 10
    
    def test_nonexistent_route(self, flask_app):
        """Test 404 for non-existent routes"""
        response = flask_app.get('/nonexistent')
        assert response.status_code == 404
    
    @patch('app.os.path.exists')
    def test_telegram_bot_running_check(self, mock_exists, flask_app):
        """Test Telegram bot running status check"""
        # Test when PID file exists
        mock_exists.return_value = True
        response = flask_app.get('/api/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['telegram_bot']['running'] is True
        
        # Test when PID file doesn't exist
        mock_exists.return_value = False
        response = flask_app.get('/api/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['telegram_bot']['running'] is False