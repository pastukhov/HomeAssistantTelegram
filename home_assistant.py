import os
import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional
from metrics import track_homeassistant_request, track_device_command

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class HomeAssistantAPI:
    def __init__(self):
        """Initialize Home Assistant API client."""
        self.base_url = os.getenv('HOME_ASSISTANT_URL', 'http://localhost:8123')
        self.token = os.getenv('HOME_ASSISTANT_TOKEN')
        
        if not self.token:
            logger.warning("HOME_ASSISTANT_TOKEN environment variable not set")
        
        # Remove trailing slash from base URL
        self.base_url = self.base_url.rstrip('/')
        
        # Set up headers
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    @track_homeassistant_request("{method}", "{endpoint}")
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to Home Assistant API."""
        try:
            url = f"{self.base_url}/api/{endpoint}"
            logger.debug(f"Making {method} request to: {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=30  # Увеличиваем timeout для больших ответов
            )
            
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as json_error:
                    logger.error(f"JSON parsing error in {method} {endpoint}: {json_error}")
                    logger.error(f"Response content length: {len(response.content)} bytes")
                    logger.error(f"Response status: {response.status_code}")
                    logger.error(f"Response headers: {dict(response.headers)}")
                    
                    # Логируем полный контекст для отладки
                    import traceback
                    logger.error(f"Call stack: {traceback.format_stack()}")
                    
                    # Попробуем обрезать ответ и попробовать снова
                    if len(response.content) > 100000:  # Если ответ больше 100KB
                        logger.warning("Response too large, trying alternative approach")
                        return None
                    else:
                        logger.error(f"Response preview: {response.text[:500]}...")
                        # Выбрасываем исключение для передачи в бот
                        raise json_error
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def get_all_states(self) -> Optional[List[Dict]]:
        """Get all entity states from Home Assistant."""
        return self._make_request('GET', 'states')
    
    def get_entity_state(self, entity_id: str) -> Optional[Dict]:
        """Get state of a specific entity."""
        return self._make_request('GET', f'states/{entity_id}')
    
    def call_service(self, domain: str, service: str, entity_id: str) -> bool:
        """Call a Home Assistant service."""
        try:
            data = {
                'entity_id': entity_id
            }
            
            url = f"{self.base_url}/api/services/{domain}/{service}"
            logger.debug(f"Calling service: {url} with data: {data}")
            
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=15
            )
            
            logger.debug(f"Service call response: {response.status_code} - {response.text[:200]}")
            
            # Home Assistant API возвращает 200 для успешных команд
            # Даже если устройство недоступно, команда может быть принята
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Service call failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Service call error: {e}")
            return False
    
    def get_lights(self) -> List[Dict]:
        """Get all light entities and their states."""
        try:
            states = self.get_all_states()
            if not states:
                logger.warning("Could not get all states, trying alternative approach")
                return self._get_lights_alternative()
            
            lights = []
            for state in states:
                entity_id = state.get('entity_id', '')
                if entity_id.startswith('light.'):
                    lights.append({
                        'entity_id': entity_id,
                        'state': state.get('state', 'unknown'),
                        'friendly_name': state.get('attributes', {}).get('friendly_name', entity_id),
                        'brightness': state.get('attributes', {}).get('brightness'),
                        'color_temp': state.get('attributes', {}).get('color_temp')
                    })
            
            return sorted(lights, key=lambda x: x['friendly_name'])
        except Exception as e:
            logger.error(f"Error in get_lights: {e}")
            return self._get_lights_alternative()
    
    def _get_lights_alternative(self) -> List[Dict]:
        """Alternative method to get lights when main API fails."""
        try:
            # Получаем список доменов сначала
            result = self._make_request('GET', 'services')
            if result is None:
                return []
            
            # Попробуем получить конкретные световые устройства через индивидуальные запросы
            lights = []
            
            # Попробуем найти известные световые устройства
            common_light_names = ['main_light', 'bedroom_light', 'kitchen_light', 'living_room_light']
            
            for light_name in common_light_names:
                entity_id = f'light.{light_name}'
                state_data = self.get_entity_state(entity_id)
                if state_data:
                    lights.append({
                        'entity_id': entity_id,
                        'state': state_data.get('state', 'unknown'),
                        'friendly_name': state_data.get('attributes', {}).get('friendly_name', entity_id),
                        'brightness': state_data.get('attributes', {}).get('brightness'),
                        'color_temp': state_data.get('attributes', {}).get('color_temp')
                    })
            
            # Если ничего не нашли, вернем пустой список с пояснением
            if not lights:
                logger.info("No lights found with alternative method")
            
            return lights
        except Exception as e:
            logger.error(f"Error in alternative lights method: {e}")
            return []
    
    def get_switches(self) -> List[Dict]:
        """Get all switch entities and their states."""
        states = self.get_all_states()
        if not states:
            return []
        
        switches = []
        for state in states:
            entity_id = state.get('entity_id', '')
            if entity_id.startswith('switch.'):
                switches.append({
                    'entity_id': entity_id,
                    'state': state.get('state', 'unknown'),
                    'friendly_name': state.get('attributes', {}).get('friendly_name', entity_id)
                })
        
        return sorted(switches, key=lambda x: x['friendly_name'])
    
    def get_sensors(self) -> List[Dict]:
        """Get all sensor entities and their states."""
        states = self.get_all_states()
        if not states:
            return []
        
        sensors = []
        for state in states:
            entity_id = state.get('entity_id', '')
            if entity_id.startswith('sensor.'):
                attributes = state.get('attributes', {})
                sensors.append({
                    'entity_id': entity_id,
                    'state': state.get('state', 'unknown'),
                    'friendly_name': attributes.get('friendly_name', entity_id),
                    'unit': attributes.get('unit_of_measurement', ''),
                    'device_class': attributes.get('device_class')
                })
        
        return sorted(sensors, key=lambda x: x['friendly_name'])
    
    @track_device_command("{entity_id}", "turn_on")
    def turn_on_light(self, entity_id: str) -> bool:
        """Turn on a light."""
        return self.call_service('light', 'turn_on', entity_id)
    
    @track_device_command("{entity_id}", "turn_off")
    def turn_off_light(self, entity_id: str) -> bool:
        """Turn off a light."""
        return self.call_service('light', 'turn_off', entity_id)
    
    @track_device_command("{entity_id}", "turn_on")
    def turn_on_switch(self, entity_id: str) -> bool:
        """Turn on a switch."""
        return self.call_service('switch', 'turn_on', entity_id)
    
    @track_device_command("{entity_id}", "turn_off")
    def turn_off_switch(self, entity_id: str) -> bool:
        """Turn off a switch."""
        return self.call_service('switch', 'turn_off', entity_id)
    
    def toggle_entity(self, entity_id: str) -> bool:
        """Toggle an entity (light or switch)."""
        if entity_id.startswith('light.'):
            return self.call_service('light', 'toggle', entity_id)
        elif entity_id.startswith('switch.'):
            return self.call_service('switch', 'toggle', entity_id)
        else:
            return False
    
    def get_current_time(self) -> str:
        """Get current timestamp."""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def test_connection(self) -> bool:
        """Test connection to Home Assistant."""
        try:
            result = self._make_request('GET', '')
            return result is not None and 'message' in result
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# Global instance for easy access
ha_api = HomeAssistantAPI()
