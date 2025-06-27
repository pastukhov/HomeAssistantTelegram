#!/usr/bin/env python3
"""
Standalone Telegram Bot Service
Runs as a separate process alongside the Flask app
"""

import os
import sys
import signal
import logging
import asyncio
from bot import start_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self):
        self.running = False
        
    def signal_handler(self, signum, frame):
        logger.info("Received shutdown signal")
        self.running = False
        sys.exit(0)
        
    def run(self):
        """Run the Telegram bot service"""
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check if bot token is available
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not telegram_token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
            return
            
        logger.info("Starting Telegram Bot Service...")
        self.running = True
        
        try:
            start_bot()
        except KeyboardInterrupt:
            logger.info("Bot service stopped by user")
        except Exception as e:
            logger.error(f"Bot service error: {e}")
            
if __name__ == "__main__":
    service = TelegramBotService()
    service.run()