#!/usr/bin/env python3
"""
Standalone Telegram Bot Runner
Runs the Telegram bot independently from the Flask web application
"""

import os
import logging
import asyncio
from bot import start_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the Telegram bot"""
    # Check if bot token is available
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    logger.info("Starting Telegram bot...")
    try:
        start_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    main()