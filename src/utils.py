import os
import logging

from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram import (
    Update,
    BotCommand,
    BotCommandScopeChat,
    MenuButtonCommands,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

logger = logging.getLogger(__name__)


def load_message(name: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    message_path = os.path.join(current_dir, 'resources', 'messages', f'{name}.txt')
    with open(message_path, "r", encoding="utf-8") as file:
        return file.read()


async def send_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    text = text.encode("utf8").decode("utf8")

    return await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
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


    logger.warning(
        "Image '%s' not found in %s. Supported extensions: %s",
        name, images_dir, extensions
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="⚠️ Картинка тимчасово недоступна"
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

def load_prompt(name: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, 'resources', 'prompts', f'{name}.txt')
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def load_translator_prompt(language_code: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(
        current_dir,
        'resources',
        'prompts',
        'translator',
        f'{language_code}.txt'
    )
    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons: dict):
    text = text.encode('utf8', errors='surrogatepass').decode('utf8')
    keyboard = []
    for key, value in buttons.items():
        button = InlineKeyboardButton(str(value), callback_data=str(key))
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return await context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text=text,
        reply_markup=reply_markup,
        message_thread_id=update.effective_message.message_thread_id
    )