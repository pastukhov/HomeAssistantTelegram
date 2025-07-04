import logging
import os

from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from home_assistant import HomeAssistantAPI

from metrics import track_telegram_command

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Home Assistant API
ha_api = HomeAssistantAPI()


@track_telegram_command("start")
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
/light_on <entity_id> - Включить свет
/light_off <entity_id> - Выключить свет

🔌 *Управление выключателями:*
/switches - Список всех выключателей
/switch_on <entity_id> - Включить выключатель
/switch_off <entity_id> - Выключить выключатель

*Примеры использования:*
`/light_on light.kitchen`
`/switch_off switch.garden_lights`

💡 *Совет:* Используйте /lights или /switches чтобы увидеть доступные устройства
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


@track_telegram_command("help")
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🤖 *Справка по командам Home Assistant Bot*

📊 *Информация о системе:*
/status - Показать статус системы Home Assistant
/sensors \[номер_страницы\] - Показания датчиков
/lights \[номер_страницы\] - Список светильников
/switches \[номер_страницы\] - Список выключателей

💡 *Управление освещением:*
/light_on <entity_id> - Включить светильник
/light_off <entity_id> - Выключить светильник

🔌 *Управление выключателями:*
/switch_on <entity_id> - Включить выключатель
/switch_off <entity_id> - Выключить выключатель

*Примеры использования:*
`/lights` - первая страница световых устройств
`/lights 2` - вторая страница
`/light_on light.kitchen` - включить свет на кухне
`/switch_off switch.garden_lights` - выключить садовое освещение

📄 *Навигация:* В списках устройств используйте ссылки ⬅️ ➡️ для перехода между страницами
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


@track_telegram_command("status")
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show Home Assistant status."""
    try:
        states = ha_api.get_all_states()
        if states:
            lights_count = len(
                [s for s in states if s.get("entity_id", "").startswith("light.")]
            )
            switches_count = len(
                [s for s in states if s.get("entity_id", "").startswith("switch.")]
            )
            sensors_count = len(
                [s for s in states if s.get("entity_id", "").startswith("sensor.")]
            )

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

        await update.message.reply_text(status_message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Status command error: {e}")
        await update.message.reply_text(f"❌ Error getting status: {str(e)}")


@track_telegram_command("lights")
async def lights(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all lights and their states with pagination."""
    try:
        # Определяем страницу из аргументов команды
        page = 1
        if context.args and context.args[0].isdigit():
            page = max(1, int(context.args[0]))

        # Отправляем сообщение о загрузке
        loading_msg = await update.message.reply_text(
            "🔄 Получаю информацию о световых устройствах..."
        )

        lights_data = ha_api.get_lights()
        if not lights_data:
            await loading_msg.edit_text(
                "💡 Световые устройства не найдены или нет подключения к Home Assistant.\n\nПопробуйте команду /status для проверки соединения."
            )
            return

        # Настройки пагинации
        per_page = 8
        total_pages = (len(lights_data) + per_page - 1) // per_page
        page = min(page, total_pages)  # Не превышаем максимальную страницу

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_lights = lights_data[start_idx:end_idx]

        message = f"💡 *Световые устройства* (стр. {page}/{total_pages}):\n\n"

        for light in page_lights:
            state_emoji = "🟢" if light["state"] == "on" else "🔴"
            if light["state"] == "unavailable":
                state_emoji = "⚫"

            friendly_name = light["friendly_name"]
            if len(friendly_name) > 25:  # Обрезаем длинные имена
                friendly_name = friendly_name[:22] + "..."

            message += f"{state_emoji} {friendly_name}\n"
            message += f"   `{light['entity_id']}`\n\n"

        # Добавляем навигацию
        nav_line = ""
        if page > 1:
            nav_line += f"⬅️ `/lights {page - 1}` | "
        nav_line += f"📄 {page}/{total_pages}"
        if page < total_pages:
            nav_line += f" | `/lights {page + 1}` ➡️"

        message += f"\n{nav_line}\n\n"
        message += f"Всего устройств: {len(lights_data)}\n\n"
        message += "_Управление:_\n"
        message += "`/light_on entity_id` - включить\n"
        message += "`/light_off entity_id` - выключить"

        await loading_msg.edit_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Lights command error: {e}")
        error_msg = "❌ Ошибка при получении информации о световых устройствах.\n\n"
        if "parse entities" in str(e).lower():
            error_msg += "Возможно, данные от Home Assistant слишком большие или содержат ошибки.\n"
        error_msg += f"Подробности: {str(e)[:100]}..."
        await update.message.reply_text(error_msg)


@track_telegram_command("light_on")
async def light_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Turn on a light."""
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите ID светового устройства.\nПример: `/light_on light.kitchen`",
            parse_mode="Markdown",
        )
        return

    entity_id = context.args[0]
    try:
        # Проверим текущее состояние устройства
        current_state = ha_api.get_entity_state(entity_id)
        if current_state and current_state.get("state") == "on":
            await update.message.reply_text(
                f"💡 Устройство `{entity_id}` уже включено", parse_mode="Markdown"
            )
            return

        result = ha_api.turn_on_light(entity_id)

        # Дополнительная проверка: проверим фактическое состояние устройства
        import time

        time.sleep(2)  # Небольшая задержка для обновления состояния

        final_state = ha_api.get_entity_state(entity_id)
        if final_state and final_state.get("state") == "on":
            await update.message.reply_text(
                f"✅ Световое устройство `{entity_id}` включено", parse_mode="Markdown"
            )
        elif result:
            await update.message.reply_text(
                f"✅ Световое устройство `{entity_id}` включено", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"❌ Не удалось включить устройство `{entity_id}`\n\nВозможные причины:\n• Устройство недоступно\n• Неверный entity_id\n• Проблемы с сетью",
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Light on command error: {e}")
        error_msg = str(e)
        if "can't find end of the entity" in error_msg:
            await update.message.reply_text(
                f"❌ Ошибка связи с Home Assistant\n\nВозможные причины:\n• Устройство недоступно\n• Временные проблемы с сетью\n• Попробуйте через несколько секунд"
            )
        else:
            await update.message.reply_text(
                f"❌ Ошибка управления освещением: {error_msg}"
            )


@track_telegram_command("light_off")
async def light_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Turn off a light."""
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите ID светового устройства.\nПример: `/light_off light.kitchen`",
            parse_mode="Markdown",
        )
        return

    entity_id = context.args[0]
    try:
        # Проверим текущее состояние устройства
        current_state = ha_api.get_entity_state(entity_id)
        if current_state and current_state.get("state") == "off":
            await update.message.reply_text(
                f"💡 Устройство `{entity_id}` уже выключено", parse_mode="Markdown"
            )
            return

        result = ha_api.turn_off_light(entity_id)

        # Дополнительная проверка: проверим фактическое состояние устройства
        import time

        time.sleep(2)  # Небольшая задержка для обновления состояния

        final_state = ha_api.get_entity_state(entity_id)
        if final_state and final_state.get("state") == "off":
            await update.message.reply_text(
                f"✅ Световое устройство `{entity_id}` выключено", parse_mode="Markdown"
            )
        elif result:
            await update.message.reply_text(
                f"✅ Световое устройство `{entity_id}` выключено", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"❌ Не удалось выключить устройство `{entity_id}`\n\nВозможные причины:\n• Устройство недоступно\n• Неверный entity_id\n• Проблемы с сетью",
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Light off command error: {e}")
        error_msg = str(e)
        if "can't find end of the entity" in error_msg:
            await update.message.reply_text(
                f"❌ Ошибка связи с Home Assistant\n\nВозможные причины:\n• Устройство недоступно\n• Временные проблемы с сетью\n• Попробуйте через несколько секунд"
            )
        else:
            await update.message.reply_text(
                f"❌ Ошибка управления освещением: {error_msg}"
            )


@track_telegram_command("switches")
async def switches(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all switches and their states with pagination."""
    try:
        # Определяем страницу из аргументов команды
        page = 1
        if context.args and context.args[0].isdigit():
            page = max(1, int(context.args[0]))

        loading_msg = await update.message.reply_text(
            "🔄 Получаю информацию о переключателях..."
        )

        switches_data = ha_api.get_switches()
        if not switches_data:
            await loading_msg.edit_text(
                "🔌 Переключатели не найдены или нет подключения к Home Assistant.\n\nПопробуйте команду /status для проверки соединения."
            )
            return

        # Настройки пагинации
        per_page = 8
        total_pages = (len(switches_data) + per_page - 1) // per_page
        page = min(page, total_pages)

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_switches = switches_data[start_idx:end_idx]

        message = f"🔌 *Переключатели* (стр. {page}/{total_pages}):\n\n"

        for switch in page_switches:
            state_emoji = "🟢" if switch["state"] == "on" else "🔴"
            if switch["state"] == "unavailable":
                state_emoji = "⚫"

            friendly_name = switch["friendly_name"]
            if len(friendly_name) > 25:
                friendly_name = friendly_name[:22] + "..."

            message += f"{state_emoji} {friendly_name}\n"
            message += f"   `{switch['entity_id']}`\n\n"

        # Добавляем навигацию
        nav_line = ""
        if page > 1:
            nav_line += f"⬅️ `/switches {page - 1}` | "
        nav_line += f"📄 {page}/{total_pages}"
        if page < total_pages:
            nav_line += f" | `/switches {page + 1}` ➡️"

        message += f"\n{nav_line}\n\n"
        message += f"Всего устройств: {len(switches_data)}\n\n"
        message += "_Управление:_\n"
        message += "`/switch_on entity_id` - включить\n"
        message += "`/switch_off entity_id` - выключить"

        await loading_msg.edit_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Switches command error: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при получении переключателей: {str(e)}"
        )


@track_telegram_command("switch_on")
async def switch_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Turn on a switch."""
    if not context.args:
        await update.message.reply_text(
            "❌ Please specify a switch entity ID.\nExample: `/switch_on switch.garden`",
            parse_mode="Markdown",
        )
        return

    entity_id = context.args[0]
    try:
        result = ha_api.turn_on_switch(entity_id)
        if result:
            await update.message.reply_text(
                f"✅ Switch `{entity_id}` turned on", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"❌ Failed to turn on switch `{entity_id}`", parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Switch on command error: {e}")
        await update.message.reply_text(f"❌ Error controlling switch: {str(e)}")


@track_telegram_command("switch_off")
async def switch_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Turn off a switch."""
    if not context.args:
        await update.message.reply_text(
            "❌ Please specify a switch entity ID.\nExample: `/switch_off switch.garden`",
            parse_mode="Markdown",
        )
        return

    entity_id = context.args[0]
    try:
        result = ha_api.turn_off_switch(entity_id)
        if result:
            await update.message.reply_text(
                f"✅ Switch `{entity_id}` turned off", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"❌ Failed to turn off switch `{entity_id}`", parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Switch off command error: {e}")
        await update.message.reply_text(f"❌ Error controlling switch: {str(e)}")


@track_telegram_command("sensors")
async def sensors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List sensor readings with pagination."""
    try:
        # Определяем страницу из аргументов команды
        page = 1
        if context.args and context.args[0].isdigit():
            page = max(1, int(context.args[0]))

        loading_msg = await update.message.reply_text(
            "🔄 Получаю показания датчиков..."
        )

        sensors_data = ha_api.get_sensors()
        if not sensors_data:
            await loading_msg.edit_text(
                "📡 Датчики не найдены или нет подключения к Home Assistant.\n\nПопробуйте команду /status для проверки соединения."
            )
            return

        # Настройки пагинации
        per_page = 6  # Меньше элементов для датчиков (больше информации)
        total_pages = (len(sensors_data) + per_page - 1) // per_page
        page = min(page, total_pages)

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_sensors = sensors_data[start_idx:end_idx]

        message = f"📡 *Показания датчиков* (стр. {page}/{total_pages}):\n\n"

        for sensor in page_sensors:
            friendly_name = sensor["friendly_name"]
            if len(friendly_name) > 25:
                friendly_name = friendly_name[:22] + "..."

            state = sensor["state"]
            unit = sensor.get("unit", "")

            # Обрезаем слишком длинные значения
            if len(str(state)) > 15:
                state = str(state)[:12] + "..."

            message += f"📊 {friendly_name}\n"
            message += f"   `{sensor['entity_id']}`\n"
            message += f"   📈 {state} {unit}\n\n"

        # Добавляем навигацию
        nav_line = ""
        if page > 1:
            nav_line += f"⬅️ `/sensors {page - 1}` | "
        nav_line += f"📄 {page}/{total_pages}"
        if page < total_pages:
            nav_line += f" | `/sensors {page + 1}` ➡️"

        message += f"\n{nav_line}\n\n"
        message += f"Всего датчиков: {len(sensors_data)}"

        await loading_msg.edit_text(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Sensors command error: {e}")
        await update.message.reply_text(f"❌ Ошибка при получении датчиков: {str(e)}")


@track_telegram_command("unknown")
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "❓ Unknown command. Use /help to see available commands."
    )


def start_bot():
    """Start the Telegram bot."""
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
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


if __name__ == "__main__":
    start_bot()
