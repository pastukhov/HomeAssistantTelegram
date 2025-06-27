import os
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from home_assistant import HomeAssistantAPI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Home Assistant API
ha_api = HomeAssistantAPI()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🏠 *Home Assistant Telegram Bot*

Добро пожаловать! Я помогу вам управлять устройствами Home Assistant через Telegram.

*Основные команды:*

📊 *Информация:*
/help - Показать справку
/status - Статус системы
/sensors - Показания датчиков

💡 *Управление освещением:*
/lights - Список всех светильников
/light\_on <entity\_id> - Включить свет
/light\_off <entity\_id> - Выключить свет

🔌 *Управление выключателями:*
/switches - Список всех выключателей
/switch\_on <entity\_id> - Включить выключатель
/switch\_off <entity\_id> - Выключить выключатель

*Примеры использования:*
`/light_on light.kitchen`
`/switch_off switch.garden_lights`

💡 *Совет:* Используйте /lights или /switches чтобы увидеть доступные устройства
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🤖 *Справка по командам Home Assistant Bot*

📊 *Информация о системе:*
/status - Показать статус системы Home Assistant
/sensors - Показать показания датчиков

💡 *Управление освещением:*
/lights - Список всех светильников и их состояние
/light\_on <entity\_id> - Включить указанный светильник
/light\_off <entity\_id> - Выключить указанный светильник

🔌 *Управление выключателями:*
/switches - Список всех выключателей и их состояние
/switch\_on <entity\_id> - Включить указанный выключатель
/switch\_off <entity\_id> - Выключить указанный выключатель

*Примеры использования:*
`/light_on light.kitchen` - включить свет на кухне
`/switch_off switch.garden_lights` - выключить садовое освещение

💡 *Совет:* Используйте команды /lights или /switches чтобы увидеть доступные устройства и их entity\_id
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show Home Assistant status."""
    try:
        states = ha_api.get_all_states()
        if states:
            lights_count = len([s for s in states if s.get('entity_id', '').startswith('light.')])
            switches_count = len([s for s in states if s.get('entity_id', '').startswith('switch.')])
            sensors_count = len([s for s in states if s.get('entity_id', '').startswith('sensor.')])
            
            status_message = f"""
🏠 *Home Assistant Status*

✅ Connected and operational
📊 Total entities: {len(states)}
💡 Lights: {lights_count}
🔌 Switches: {switches_count}
📡 Sensors: {sensors_count}

🕐 Last updated: {ha_api.get_current_time()}
            """
        else:
            status_message = "❌ Unable to connect to Home Assistant"
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Status command error: {e}")
        await update.message.reply_text(f"❌ Error getting status: {str(e)}")

async def lights(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all lights and their states."""
    try:
        lights_data = ha_api.get_lights()
        if not lights_data:
            await update.message.reply_text("💡 No lights found or unable to connect to Home Assistant")
            return
        
        message = "💡 *Lights Status:*\n\n"
        for light in lights_data[:15]:  # Limit to 15 lights to avoid message length issues
            state_emoji = "🟢" if light['state'] == 'on' else "🔴"
            message += f"{state_emoji} `{light['entity_id']}`\n"
            message += f"   📝 {light['friendly_name']}\n"
            message += f"   🔧 State: {light['state']}\n\n"
        
        if len(lights_data) > 15:
            message += f"... and {len(lights_data) - 15} more lights"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Lights command error: {e}")
        await update.message.reply_text(f"❌ Error getting lights: {str(e)}")

async def light_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Turn on a light."""
    if not context.args:
        await update.message.reply_text("❌ Please specify a light entity ID.\nExample: `/light_on light.kitchen`", parse_mode='Markdown')
        return
    
    entity_id = context.args[0]
    try:
        result = ha_api.turn_on_light(entity_id)
        if result:
            await update.message.reply_text(f"✅ Light `{entity_id}` turned on", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Failed to turn on light `{entity_id}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Light on command error: {e}")
        await update.message.reply_text(f"❌ Error controlling light: {str(e)}")

async def light_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Turn off a light."""
    if not context.args:
        await update.message.reply_text("❌ Please specify a light entity ID.\nExample: `/light_off light.kitchen`", parse_mode='Markdown')
        return
    
    entity_id = context.args[0]
    try:
        result = ha_api.turn_off_light(entity_id)
        if result:
            await update.message.reply_text(f"✅ Light `{entity_id}` turned off", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Failed to turn off light `{entity_id}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Light off command error: {e}")
        await update.message.reply_text(f"❌ Error controlling light: {str(e)}")

async def switches(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all switches and their states."""
    try:
        switches_data = ha_api.get_switches()
        if not switches_data:
            await update.message.reply_text("🔌 No switches found or unable to connect to Home Assistant")
            return
        
        message = "🔌 *Switches Status:*\n\n"
        for switch in switches_data[:15]:  # Limit to 15 switches
            state_emoji = "🟢" if switch['state'] == 'on' else "🔴"
            message += f"{state_emoji} `{switch['entity_id']}`\n"
            message += f"   📝 {switch['friendly_name']}\n"
            message += f"   🔧 State: {switch['state']}\n\n"
        
        if len(switches_data) > 15:
            message += f"... and {len(switches_data) - 15} more switches"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Switches command error: {e}")
        await update.message.reply_text(f"❌ Error getting switches: {str(e)}")

async def switch_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Turn on a switch."""
    if not context.args:
        await update.message.reply_text("❌ Please specify a switch entity ID.\nExample: `/switch_on switch.garden`", parse_mode='Markdown')
        return
    
    entity_id = context.args[0]
    try:
        result = ha_api.turn_on_switch(entity_id)
        if result:
            await update.message.reply_text(f"✅ Switch `{entity_id}` turned on", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Failed to turn on switch `{entity_id}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Switch on command error: {e}")
        await update.message.reply_text(f"❌ Error controlling switch: {str(e)}")

async def switch_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Turn off a switch."""
    if not context.args:
        await update.message.reply_text("❌ Please specify a switch entity ID.\nExample: `/switch_off switch.garden`", parse_mode='Markdown')
        return
    
    entity_id = context.args[0]
    try:
        result = ha_api.turn_off_switch(entity_id)
        if result:
            await update.message.reply_text(f"✅ Switch `{entity_id}` turned off", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Failed to turn off switch `{entity_id}`", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Switch off command error: {e}")
        await update.message.reply_text(f"❌ Error controlling switch: {str(e)}")

async def sensors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List sensor readings."""
    try:
        sensors_data = ha_api.get_sensors()
        if not sensors_data:
            await update.message.reply_text("📡 No sensors found or unable to connect to Home Assistant")
            return
        
        message = "📡 *Sensor Readings:*\n\n"
        for sensor in sensors_data[:10]:  # Limit to 10 sensors
            message += f"📊 `{sensor['entity_id']}`\n"
            message += f"   📝 {sensor['friendly_name']}\n"
            message += f"   📈 Value: {sensor['state']} {sensor.get('unit', '')}\n\n"
        
        if len(sensors_data) > 10:
            message += f"... and {len(sensors_data) - 10} more sensors"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Sensors command error: {e}")
        await update.message.reply_text(f"❌ Error getting sensors: {str(e)}")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "❓ Unknown command. Use /help to see available commands."
    )

def start_bot():
    """Start the Telegram bot."""
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    # Create the Application
    application = Application.builder().token(bot_token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("lights", lights))
    application.add_handler(CommandHandler("light_on", light_on))
    application.add_handler(CommandHandler("light_off", light_off))
    application.add_handler(CommandHandler("switches", switches))
    application.add_handler(CommandHandler("switch_on", switch_on))
    application.add_handler(CommandHandler("switch_off", switch_off))
    application.add_handler(CommandHandler("sensors", sensors))
    
    # Handle unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Start the bot
    logger.info("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    start_bot()
