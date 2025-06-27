import logging
import threading
import os
from app import app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_flask():
    """Run Flask application"""
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

def run_bot():
    """Run Telegram bot"""
    try:
        # Import bot here to avoid startup issues
        from bot import start_bot
        start_bot()
    except ImportError as e:
        logger.error(f"Telegram bot dependencies not available: {e}")
        logger.info("Running in web-only mode. Install python-telegram-bot to enable bot functionality.")
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    # Check if we should run bot
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if telegram_token:
        # Start Flask app in a separate thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Start Telegram bot in main thread
        logger.info("Starting Telegram bot and Flask web interface...")
        run_bot()
    else:
        # Run only Flask web interface
        logger.info("TELEGRAM_BOT_TOKEN not set. Running web interface only.")
        logger.info("Set TELEGRAM_BOT_TOKEN to enable Telegram bot functionality.")
        run_flask()
