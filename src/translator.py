import logging

from telegram import Update
from telegram.ext import ContextTypes

from utils import (
    send_text,
    send_text_buttons,
    load_translator_prompt,
    send_image
)

from gpt import ChatGPTService
from config import CHATGPT_TOKEN

logger = logging.getLogger(__name__)

chatgpt_service = ChatGPTService(CHATGPT_TOKEN)

async def translator(update: Update, context: ContextTypes.DEFAULT_TYPE, start_func=None):
    context.user_data.clear()
    context.user_data["conversation_state"] = "translator"

    await send_image(update, context, "translator")

    buttons = {
        "translate_en": "English 🇬🇧",
        "translate_uk": "Українська 🇺🇦",
        "translate_de": "Deutsch 🇩🇪",
        "start": "Закінчити",
    }

    await send_text_buttons(
        update,
        context,
        "🌍 Оберіть мову перекладу:",
        buttons,
    )

async def translator_button(update: Update, context: ContextTypes.DEFAULT_TYPE, start_func=None):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        context.user_data.clear()
        if start_func:
            await start_func(update, context)
        else:
            await update.message.reply_text("Помилка: функція start не знайдена")
        return

    if query.data == "translator":
        context.user_data.clear()
        await translator(update, context)
        return

    language_map = {
        "translate_en": ("en", "English"),
        "translate_uk": ("uk", "Українська"),
        "translate_de": ("de", "Deutsch"),
    }

    lang_code, lang_name = language_map[query.data]

    context.user_data["conversation_state"] = "translator"
    context.user_data["lang_code"] = lang_code
    context.user_data["lang_name"] = lang_name

    await send_text(
        update,
        context,
        f"✏️ Надішліть текст для перекладу на {lang_name}:",
    )

async def handle_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_code = context.user_data.get("lang_code")
    lang_name = context.user_data.get("lang_name")

    if not lang_code:
        await send_text(update, context, "Спочатку оберіть мову перекладу.")
        return

    message_text = update.message.text
    if not message_text:
        await send_text(update, context, "Будь ласка, надішліть текст для перекладу.")
        return

    waiting_message = await send_text(update, context, "⏳ Перекладаю...")

    try:
        prompt = load_translator_prompt(lang_code)
        chatgpt_service.set_prompt(prompt)

        translated_text = await chatgpt_service.add_message(message_text)

        buttons = {
            "translator": "🔁 Змінити мову",
            "start": "Закінчити"
        }

        await send_text_buttons(
            update,
            context,
            f"🌍 Переклад ({lang_name}):\n\n{translated_text}",
            buttons
        )

    except Exception as e:
        logger.error(f"Translator error: {e}")
        await send_text(update, context, "❌ Помилка при перекладі.")

    finally:
        if 'waiting_message' in locals():
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=waiting_message.message_id
                )
            except Exception as e:
                logger.error(f"Error deleting waiting message: {e}")
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=waiting_message.message_id
        )

    return
