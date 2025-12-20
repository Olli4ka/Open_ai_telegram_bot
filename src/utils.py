import os
import logging

from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram import Update, BotCommand, BotCommandScopeChat, MenuButtonCommands

logger = logging.getLogger(__name__)


def load_message(name: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    message_path = os.path.join(current_dir, 'resources', 'messages', f'{name}.txt')
    with open(message_path, "r", encoding="utf-8") as file:
        return file.read()


async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    text = text.encode('utf8').decode('utf8')
    return await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN
    )


async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(current_dir, 'resources', 'images')

    extensions = ('.jpg', '.jpeg', '.png', '.webp')

    for ext in extensions:
        image_path = os.path.join(images_dir, f'{name}{ext}')
        if os.path.exists(image_path):
            with open(image_path, 'rb') as image:
                return await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=image
                )

    # логируем, но НЕ падаем
    logger.warning(
        "Image '%s' not found in %s. Supported extensions: %s",
        name, images_dir, extensions
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="⚠️ Картинка временно недоступна"
    )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, commands: dict):
    command_list = [
        BotCommand(command=key, description=value)
        for key, value in commands.items()
    ]
    await context.bot.set_my_commands(
        command_list,
        scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )
    await context.bot.set_chat_menu_button(
        menu_button=MenuButtonCommands(),
        chat_id=update.effective_chat.id
    )
