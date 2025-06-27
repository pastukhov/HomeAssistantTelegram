import logging
import subprocess
import os
import atexit
from app import app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global variable to track bot process
bot_process = None

def start_telegram_bot():
    """Start Telegram bot as a separate process"""
    global bot_process
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not telegram_token:
        logger.info("TELEGRAM_BOT_TOKEN not set. Telegram bot disabled.")
        return
        
    try:
        # Start bot as separate process
        bot_process = subprocess.Popen(
            ['python', 'telegram_bot_service.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info(f"Telegram bot started with PID: {bot_process.pid}")
        
        # Write PID to file for later cleanup
        with open('telegram_bot.pid', 'w') as f:
            f.write(str(bot_process.pid))
            
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")

def cleanup_bot_process():
    """Clean up bot process on exit"""
    global bot_process
    if bot_process and bot_process.poll() is None:
        logger.info("Stopping Telegram bot...")
        bot_process.terminate()
        bot_process.wait()

# Register cleanup function
atexit.register(cleanup_bot_process)

# Start Telegram bot when module is imported
start_telegram_bot()

# This ensures the Flask app runs for gunicorn
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
