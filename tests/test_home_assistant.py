"""
Tests for Home Assistant API client
"""

from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests

from home_assistant import HomeAssistantAPI


class TestHomeAssistantAPI:
    """Test cases for Home Assistant API client"""

    def test_init(self):
        """Test HomeAssistantAPI initialization"""
        ha = HomeAssistantAPI()
        assert ha.base_url == "http://test-ha.local:8123"
        assert ha.token == "test_token_123"
        assert "Bearer test_token_123" in ha.headers["Authorization"]

    @patch.object(HomeAssistantAPI, "_make_request")
    def test_get_all_states_success(self, mock_make_request):
        """Test successful API call to get all states"""
        mock_make_request.return_value = [
            {"entity_id": "light.test", "state": "on"},
            {"entity_id": "switch.test", "state": "off"},
        ]

        ha = HomeAssistantAPI()
        result = ha.get_all_states()

        assert result is not None
        assert len(result) == 2
        assert result[0]["entity_id"] == "light.test"
        mock_make_request.assert_called_once_with("GET", "/api/states")

    @patch.object(HomeAssistantAPI, "_make_request")
    def test_get_all_states_failure(self, mock_make_request):
        """Test API call failure"""
        mock_make_request.return_value = None

        ha = HomeAssistantAPI()
        result = ha.get_all_states()

        assert result is None

    @patch.object(HomeAssistantAPI, "_make_request")
    def test_call_service_success(self, mock_make_request):
        """Test successful service call"""
        mock_make_request.return_value = {"success": True}

        ha = HomeAssistantAPI()
        result = ha.call_service("light", "turn_on", "light.test")

        assert result is True
        expected_data = {"entity_id": "light.test"}
        mock_make_request.assert_called_once_with(
            "POST", "/api/services/light/turn_on", expected_data
        )

    @patch.object(HomeAssistantAPI, "_make_request")
    def test_call_service_failure(self, mock_make_request):
        """Test failed service call"""
        mock_make_request.return_value = None

        ha = HomeAssistantAPI()
        result = ha.call_service("light", "turn_on", "light.test")

        assert result is False

    @patch.object(HomeAssistantAPI, "get_all_states")
    def test_get_lights(self, mock_get_states):
        """Test filtering lights from all states"""
        mock_get_states.return_value = [
            {
                "entity_id": "light.bedroom",
                "state": "on",
                "attributes": {"friendly_name": "Bedroom Light"},
            },
            {
                "entity_id": "switch.fan",
                "state": "off",
                "attributes": {"friendly_name": "Fan Switch"},
            },
            {
                "entity_id": "light.kitchen",
                "state": "off",
                "attributes": {"friendly_name": "Kitchen Light"},
            },
        ]

        ha = HomeAssistantAPI()
        lights = ha.get_lights()

        assert len(lights) == 2
        assert all("light." in light["entity_id"] for light in lights)

    @patch.object(HomeAssistantAPI, "get_all_states")
    def test_get_switches(self, mock_get_states):
        """Test filtering switches from all states"""
        mock_get_states.return_value = [
            {
                "entity_id": "light.bedroom",
                "state": "on",
                "attributes": {"friendly_name": "Bedroom Light"},
            },
            {
                "entity_id": "switch.fan",
                "state": "off",
                "attributes": {"friendly_name": "Fan Switch"},
            },
            {
                "entity_id": "switch.pump",
                "state": "on",
                "attributes": {"friendly_name": "Water Pump"},
            },
        ]

        ha = HomeAssistantAPI()
        switches = ha.get_switches()

        assert len(switches) == 2
        assert all("switch." in switch["entity_id"] for switch in switches)

    @patch.object(HomeAssistantAPI, "get_all_states")
    def test_get_sensors(self, mock_get_states):
        """Test filtering sensors from all states"""
        mock_get_states.return_value = [
            {
                "entity_id": "sensor.temperature",
                "state": "22.5",
                "attributes": {
                    "friendly_name": "Temperature",
                    "unit_of_measurement": "°C",
                },
            },
            {
                "entity_id": "light.bedroom",
                "state": "on",
                "attributes": {"friendly_name": "Bedroom Light"},
            },
            {
                "entity_id": "sensor.humidity",
                "state": "45",
                "attributes": {"friendly_name": "Humidity", "unit_of_measurement": "%"},
            },
        ]

        ha = HomeAssistantAPI()
        sensors = ha.get_sensors()

        assert len(sensors) == 2
        assert all("sensor." in sensor["entity_id"] for sensor in sensors)

    @patch.object(HomeAssistantAPI, "call_service")
    def test_turn_on_light(self, mock_call_service):
        """Test turning on a light"""
        mock_call_service.return_value = True

        ha = HomeAssistantAPI()
        result = ha.turn_on_light("light.test")

        assert result is True
        mock_call_service.assert_called_with("light", "turn_on", "light.test")

    @patch.object(HomeAssistantAPI, "call_service")
    def test_turn_off_light(self, mock_call_service):
        """Test turning off a light"""
        mock_call_service.return_value = True

        ha = HomeAssistantAPI()
        result = ha.turn_off_light("light.test")

        assert result is True
        mock_call_service.assert_called_with("light", "turn_off", "light.test")

    @patch.object(HomeAssistantAPI, "_make_request")
    def test_test_connection_success(self, mock_make_request):
        """Test successful connection test"""
        mock_make_request.return_value = {"success": True}

        ha = HomeAssistantAPI()
        result = ha.test_connection()

        assert result is True

    @patch.object(HomeAssistantAPI, "_make_request")
    def test_test_connection_failure(self, mock_make_request):
        """Test failed connection test"""
        mock_make_request.return_value = None

        ha = HomeAssistantAPI()
        result = ha.test_connection()

        assert result is False
