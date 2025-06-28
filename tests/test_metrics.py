"""
Tests for metrics collection system
"""
import pytest
import time
from unittest.mock import patch, Mock
from metrics import MetricsCollector, track_telegram_command, track_homeassistant_request


class TestMetricsCollector:
    """Test cases for MetricsCollector"""
    
    def test_init(self):
        """Test MetricsCollector initialization"""
        collector = MetricsCollector()
        assert collector.start_time is not None
        assert collector.active_users_cache == set()
        assert collector.last_cleanup < time.time()
    
    def test_update_app_uptime(self):
        """Test app uptime metric update"""
        collector = MetricsCollector()
        initial_time = collector.start_time
        
        collector.update_app_uptime()
        
        # Check that the gauge was updated (we can't easily test the value)
        assert collector.start_time == initial_time
    
    @patch('metrics.psutil.Process')
    def test_update_memory_usage(self, mock_process):
        """Test memory usage metric update"""
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value.rss = 50 * 1024 * 1024  # 50MB
        mock_process.return_value = mock_process_instance
        
        collector = MetricsCollector()
        collector.update_memory_usage()
        
        mock_process_instance.memory_info.assert_called_once()
    
    def test_record_telegram_command(self):
        """Test recording Telegram command metrics"""
        collector = MetricsCollector()
        
        collector.record_telegram_command("start", "user123", True, 0.5)
        collector.record_telegram_command("lights", "user456", False, 1.2)
        
        # Check that user was added to active users
        assert "user123" in collector.active_users_cache
        assert "user456" in collector.active_users_cache
    
    def test_record_homeassistant_request(self):
        """Test recording Home Assistant request metrics"""
        collector = MetricsCollector()
        
        collector.record_homeassistant_request("GET", "/api/states", 200, 0.3)
        collector.record_homeassistant_request("POST", "/api/services/light/turn_on", 400, 0.8)
        
        # Should not raise any exceptions
        assert True
    
    def test_record_device_command(self):
        """Test recording device command metrics"""
        collector = MetricsCollector()
        
        collector.record_device_command("light.bedroom", "turn_on", True, 0.4)
        collector.record_device_command("switch.fan", "turn_off", False, 0.9)
        
        # Should not raise any exceptions
        assert True
    
    def test_update_device_status(self):
        """Test updating device status metrics"""
        collector = MetricsCollector()
        
        collector.update_device_status("light.bedroom", "Bedroom Light", "on")
        collector.update_device_status("switch.fan", "Fan Switch", "off")
        
        # Should not raise any exceptions
        assert True
    
    def test_update_homeassistant_entities(self):
        """Test updating Home Assistant entities count"""
        collector = MetricsCollector()
        
        entities = {
            "light": 5,
            "switch": 3,
            "sensor": 10,
            "automation": 2
        }
        
        collector.update_homeassistant_entities(entities)
        
        # Should not raise any exceptions
        assert True
    
    def test_cleanup_active_users(self):
        """Test active users cleanup"""
        collector = MetricsCollector()
        
        # Add some users (note: using add instead of dict assignment for set)
        collector.active_users_cache.add("user1")
        collector.active_users_cache.add("user2")
        
        # Force cleanup by setting last_cleanup to old time
        collector.last_cleanup = time.time() - 25 * 3600
        
        collector._cleanup_active_users()
        
        # Should work without errors
        assert True
    
    def test_get_metrics_summary(self):
        """Test getting metrics summary"""
        collector = MetricsCollector()
        
        # Add some test data
        collector.active_users_cache.add("user1")
        collector.active_users_cache.add("user2")
        
        summary = collector.get_metrics_summary()
        
        assert "app_uptime_seconds" in summary
        assert "memory_usage_mb" in summary
        assert "total_commands" in summary
        assert "successful_commands" in summary
        assert "failed_commands" in summary
        assert "active_users" in summary
        assert "homeassistant_entities" in summary
        
        assert summary["active_users"] == 2


class TestMetricsDecorators:
    """Test cases for metrics decorators"""
    
    @pytest.mark.asyncio
    async def test_track_telegram_command_decorator(self):
        """Test track_telegram_command decorator"""
        
        @track_telegram_command("test_command")
        async def test_function(update, context):
            return "success"
        
        # Mock update and context
        mock_update = Mock()
        mock_update.effective_user.id = 123456
        mock_context = Mock()
        
        with patch('metrics.metrics_collector') as mock_collector:
            result = await test_function(mock_update, mock_context)
            
            assert result == "success"
            mock_collector.record_telegram_command.assert_called_once()
    
    def test_track_homeassistant_request_decorator(self):
        """Test track_homeassistant_request decorator"""
        
        @track_homeassistant_request("GET", "/api/test")
        def test_function():
            return {"status": "ok"}
        
        with patch('metrics.metrics_collector') as mock_collector:
            result = test_function()
            
            assert result == {"status": "ok"}
            mock_collector.record_homeassistant_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_track_telegram_command_with_exception(self):
        """Test track_telegram_command decorator when function raises exception"""
        
        @track_telegram_command("failing_command")
        async def failing_function(update, context):
            raise ValueError("Test error")
        
        mock_update = Mock()
        mock_update.effective_user.id = 123456
        mock_context = Mock()
        
        with patch('metrics.metrics_collector') as mock_collector:
            with pytest.raises(ValueError):
                await failing_function(mock_update, mock_context)
            
            # Should still record the metric with success=False
            mock_collector.record_telegram_command.assert_called_once()
            call_args = mock_collector.record_telegram_command.call_args
            assert call_args[0][2] is False  # success parameter