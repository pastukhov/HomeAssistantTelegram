import os
import logging
from flask import Flask, render_template, jsonify
from home_assistant import HomeAssistantAPI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key")

# Initialize Home Assistant API
ha_api = HomeAssistantAPI()

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get basic system info
        states = ha_api.get_all_states()
        system_info = {
            'total_entities': len(states) if states else 0,
            'lights': len([s for s in states if s.get('entity_id', '').startswith('light.')]) if states else 0,
            'switches': len([s for s in states if s.get('entity_id', '').startswith('switch.')]) if states else 0,
            'sensors': len([s for s in states if s.get('entity_id', '').startswith('sensor.')]) if states else 0
        }
        
        # Get recent light states
        recent_lights = []
        if states:
            lights = [s for s in states if s.get('entity_id', '').startswith('light.')][:10]
            for light in lights:
                recent_lights.append({
                    'entity_id': light.get('entity_id', 'Unknown'),
                    'state': light.get('state', 'Unknown'),
                    'friendly_name': light.get('attributes', {}).get('friendly_name', light.get('entity_id', 'Unknown'))
                })
        
        return render_template('index.html', 
                             system_info=system_info, 
                             recent_lights=recent_lights,
                             ha_connected=True)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('index.html', 
                             system_info={'total_entities': 0, 'lights': 0, 'switches': 0, 'sensors': 0},
                             recent_lights=[],
                             ha_connected=False,
                             error=str(e))

@app.route('/api/status')
def api_status():
    """API endpoint for bot status"""
    try:
        states = ha_api.get_all_states()
        return jsonify({
            'status': 'connected',
            'entities_count': len(states) if states else 0,
            'timestamp': ha_api.get_current_time()
        })
    except Exception as e:
        logger.error(f"API status error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': None
        }), 500

@app.route('/api/lights')
def api_lights():
    """API endpoint for lights status"""
    try:
        lights = ha_api.get_lights()
        return jsonify({
            'status': 'success',
            'lights': lights
        })
    except Exception as e:
        logger.error(f"API lights error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
