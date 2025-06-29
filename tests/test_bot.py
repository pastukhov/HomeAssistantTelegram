"""
Tests for Telegram bot functionality
"""

from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from bot import help_command
from bot import light_off
from bot import light_on
from bot import lights
from bot import sensors
from bot import start
from bot import status
from bot import switches


class TestTelegramBot:
    """Test cases for Telegram bot commands"""

    @pytest.mark.asyncio
    async def test_start_command(self, mock_update, mock_context):
        """Test /start command"""
        await start(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Добро пожаловать" in call_args
        assert "/help" in call_args

    @pytest.mark.asyncio
    async def test_help_command(self, mock_update, mock_context):
        """Test /help command"""
        await help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Доступные команды" in call_args
        assert "/lights" in call_args
        assert "/switches" in call_args

    @pytest.mark.asyncio
    @patch("bot.ha_client")
    async def test_status_command_success(
        self, mock_ha_client, mock_update, mock_context
    ):
        """Test /status command with successful connection"""
        mock_ha_client.test_connection.return_value = True
        mock_ha_client.get_all_states.return_value = [
            {"entity_id": "light.test", "state": "on"},
            {"entity_id": "switch.test", "state": "off"},
        ]

        await status(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "✅ Соединение с Home Assistant: OK" in call_args
        assert "📊 Всего устройств:" in call_args

    @pytest.mark.asyncio
    @patch("bot.ha_client")
    async def test_status_command_failure(
        self, mock_ha_client, mock_update, mock_context
    ):
        """Test /status command with connection failure"""
        mock_ha_client.test_connection.return_value = False

        await status(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "❌ Соединение с Home Assistant: ОШИБКА" in call_args

    @pytest.mark.asyncio
    @patch("bot.ha_client")
    async def test_lights_command(self, mock_ha_client, mock_update, mock_context):
        """Test /lights command"""
        mock_ha_client.get_lights.return_value = [
            {
                "entity_id": "light.bedroom",
                "state": "on",
                "attributes": {"friendly_name": "Bedroom Light"},
            },
            {
                "entity_id": "light.kitchen",
                "state": "off",
                "attributes": {"friendly_name": "Kitchen Light"},
            },
        ]

        await lights(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "💡 Освещение" in call_args
        assert "Bedroom Light: ✅ Включен" in call_args
        assert "Kitchen Light: ❌ Выключен" in call_args

    @pytest.mark.asyncio
    @patch("bot.ha_client")
    async def test_light_on_command_success(
        self, mock_ha_client, mock_update, mock_context
    ):
        """Test successful /light_on command"""
        mock_context.args = ["light.bedroom"]
        mock_ha_client.get_entity_state.return_value = {
            "entity_id": "light.bedroom",
            "state": "off",
            "attributes": {"friendly_name": "Bedroom Light"},
        }
        mock_ha_client.turn_on_light.return_value = True

        await light_on(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "✅ Свет включен: Bedroom Light" in call_args

    @pytest.mark.asyncio
    @patch("bot.ha_client")
    async def test_light_on_already_on(self, mock_ha_client, mock_update, mock_context):
        """Test /light_on command when light is already on"""
        mock_context.args = ["light.bedroom"]
        mock_ha_client.get_entity_state.return_value = {
            "entity_id": "light.bedroom",
            "state": "on",
            "attributes": {"friendly_name": "Bedroom Light"},
        }

        await light_on(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "💡 Свет уже включен: Bedroom Light" in call_args

    @pytest.mark.asyncio
    @patch("bot.ha_client")
    async def test_light_off_command_success(
        self, mock_ha_client, mock_update, mock_context
    ):
        """Test successful /light_off command"""
        mock_context.args = ["light.bedroom"]
        mock_ha_client.get_entity_state.return_value = {
            "entity_id": "light.bedroom",
            "state": "on",
            "attributes": {"friendly_name": "Bedroom Light"},
        }
        mock_ha_client.turn_off_light.return_value = True

        await light_off(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "❌ Свет выключен: Bedroom Light" in call_args

    @pytest.mark.asyncio
    @patch("bot.ha_client")
    async def test_switches_command(self, mock_ha_client, mock_update, mock_context):
        """Test /switches command"""
        mock_ha_client.get_switches.return_value = [
            {
                "entity_id": "switch.fan",
                "state": "on",
                "attributes": {"friendly_name": "Fan Switch"},
            }
        ]

        await switches(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "🔌 Переключатели" in call_args
        assert "Fan Switch: ✅ Включен" in call_args

    @pytest.mark.asyncio
    @patch("bot.ha_client")
    async def test_sensors_command(self, mock_ha_client, mock_update, mock_context):
        """Test /sensors command"""
        mock_ha_client.get_sensors.return_value = [
            {
                "entity_id": "sensor.temperature",
                "state": "22.5",
                "attributes": {
                    "friendly_name": "Temperature",
                    "unit_of_measurement": "°C",
                },
            }
        ]

        await sensors(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "📊 Датчики" in call_args
        assert "Temperature: 22.5°C" in call_args

    @pytest.mark.asyncio
    async def test_light_on_no_args(self, mock_update, mock_context):
        """Test /light_on command without arguments"""
        mock_context.args = []

        await light_on(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Укажите ID света" in call_args
        assert "/light_on light.bedroom" in call_args

    @pytest.mark.asyncio
    async def test_light_off_no_args(self, mock_update, mock_context):
        """Test /light_off command without arguments"""
        mock_context.args = []

        await light_off(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Укажите ID света" in call_args
        assert "/light_off light.bedroom" in call_args
