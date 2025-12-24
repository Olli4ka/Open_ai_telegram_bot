import logging
from random import choice

from telegram import Update
from telegram.ext import ContextTypes

from utils import (
    send_image,
    send_text,
    load_message,
    show_main_menu,
    load_prompt,
    load_translator_prompt,
    send_text_buttons,
)

from gpt import ChatGPTService
from config import CHATGPT_TOKEN

chatgpt_service = ChatGPTService(CHATGPT_TOKEN)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start command received")

    await send_image(update, context, "start")
    await send_text(update, context, load_message("start"))
    await show_main_menu(
        update,
        context,
        {
            'start': 'Головне меню',
            'random': 'Дізнатися випадковий факт',
            'gpt': 'Запитати ChatGPT',
            'talk': 'Діалог з відомою особистістю',
            'translator': 'Перекладач',
        }
    )

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, "random")
    message_to_delete = await send_text(update, context, "Шукаю випадковий факт ...")
    try:
        prompt = load_prompt("random")
        fact = await chatgpt_service.send_question(
            prompt_text=prompt,
            message_text="Розкажи про випадковий факт"
        )
        buttons = {
            'random': 'Хочу ще один факт',
            'start': 'Закінчити'
        }
        await send_text_buttons(update, context, fact, buttons)
    except Exception as e:
        logger.error(f"Помилка в обробнику /random: {e}")
        await send_text(update, context, "Помилка при отриманні випадкового факту.")
    finally:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=message_to_delete.message_id
        )


async def random_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'random':
        await random(update, context)
    elif data == 'start':
        await start(update, context)

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await send_image(update, context, "gpt")
    chatgpt_service.set_prompt(load_prompt("gpt"))
    await send_text(update, context, "Задайте питання ...")
    context.user_data["conversation_state"] = "gpt"


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    conversation_state = context.user_data.get("conversation_state")

    if conversation_state == "gpt":
        waiting_message = await send_text(update, context, "...")
        try:
            response = await chatgpt_service.add_message(message_text)
            await send_text(update, context, response)
        except Exception as e:
            logger.error(f"Помилка при отриманні відповіді від ChatGPT: {e}")
            await send_text(update, context, "Виникла помилка при обробці вашого повідомлення.")
        finally:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=waiting_message.message_id
            )
        return

    if conversation_state == "talk":
        personality = context.user_data.get("selected_personality")
        if not personality:
            await send_text(update, context, "Спочатку оберіть особистість для розмови!")
            return

        prompt = load_prompt(personality)
        chatgpt_service.set_prompt(prompt)

        waiting_message = await send_text(update, context, "...")
        try:
            response = await chatgpt_service.add_message(message_text)
            buttons = {"start": "Закінчити"}
            personality_name = personality.replace("talk_", "").replace("_", " ").title()
            await send_text_buttons(
                update,
                context,
                f"{personality_name}: {response}",
                buttons
            )
        except Exception as e:
            logger.error(f"Помилка при отриманні відповіді від ChatGPT: {e}")
            await send_text(update, context, "Виникла помилка при отриманні відповіді!")
        finally:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=waiting_message.message_id
            )
        return

    if conversation_state == "translator":
        lang_code = context.user_data.get("lang_code")
        lang_name = context.user_data.get("lang_name")

        if not lang_code:
            await send_text(update, context, "Спочатку оберіть мову перекладу.")
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
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=waiting_message.message_id
            )

        return

    intent_recognized = await inter_random_input(update, context, message_text)
    if not intent_recognized:
        await show_funny_response(update, context)


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await send_image(update, context, "talk")
    personalities = {
        'talk_linus_torvalds': "Linus Torvalds (Linux, Git)",
        'talk_guido_van_rossum': "Guido van Rossum (Python)",
        'talk_mark_zuckerberg': "Mark Zuckerberg (Meta, Facebook)",
        'start': "Закінчити",
    }
    await send_text_buttons(update, context, "Оберіть особистість для спілкування ...", personalities)

async def talk_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "start":
        context.user_data.pop("conversation_state", None)
        context.user_data.pop("selected_personality", None)
        await start(update, context)
        return
    if data.startswith("talk_"):
        context.user_data.clear()
        context.user_data["selected_personality"] = data
        context.user_data["conversation_state"] = "talk"
        prompt = load_prompt(data)
        chatgpt_service.set_prompt(prompt)
        personality_name = data.replace("talk_", "").replace("_", " ").title()
        await send_image(update, context, data)
        buttons = {'start': "Закінчити"}
        await send_text_buttons(
            update,
            context,
            f"Hello, I`m {personality_name}."
            f"\nI heard you wanted to ask me something. "
            f"\nYou can ask questions in your native language.",
            buttons
        )

async def translator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
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

async def translator_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        context.user_data.clear()
        await start(update, context)
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

async def inter_random_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message_text: str
) -> bool:
    message_text_lower = message_text.lower()

    if any(keyword in message_text_lower for keyword in [
        'факт', 'цікав', 'random', 'випадков'
    ]):
        await send_text(
            update,
            context,
            "Схоже, ви цікавитесь випадковими фактами! Зараз покажу вам один..."
        )
        await random(update, context)
        return True

    elif any(keyword in message_text_lower for keyword in [
        'gpt', 'чат', 'питання', 'запита', 'дізнатися'
    ]):
        await send_text(
            update,
            context,
            "Схоже, у вас є питання! Переходимо до режиму спілкування з ChatGPT..."
        )
        await gpt(update, context)
        return True

    elif any(keyword in message_text_lower for keyword in [
        'розмов', 'говори', 'спілкува', 'особист', 'talk'
    ]):
        await send_text(
            update,
            context,
            "Схоже, ви хочете поговорити з відомою особистістю! Зараз покажу вам доступні варіанти..."
        )
        await talk(update, context)
        return True

    elif any(keyword in message_text_lower for keyword in [
        'переведи', 'перевод', 'переклади',
        'translate', 'translation',
        'на англий', 'на англій',
        'на немец', 'на німец',
        'translator'
    ]):
        await send_text(
            update,
            context,
            "Схоже, ви хочете перекласти текст. Оберіть мову перекладу 👇"
        )
        await translator(update, context)
        return True

    return False


async def show_funny_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    funny_responses = [
        "Хмм... Цікаво, але я не зрозумів, що саме ви хочете. Може спробуєте одну з команд з меню?",
        "Дуже цікаве повідомлення! Але мені потрібні чіткіші інструкції. Ось доступні команди:",
        "Ой, здається, ви мене застали зненацька! Я вмію багато чого, але мені потрібна конкретна команда:",
        "Вибачте, мої алгоритми не розпізнали це як команду. Ось що я точно вмію:",
        "Це повідомлення таке ж загадкове, як єдиноріг у дикій природі! Спробуйте одну з цих команд:",
        "Я намагаюся зрозуміти ваше повідомлення... Але краще скористайтесь однією з команд:",
        "О! Випадкове повідомлення! Я теж вмію бути випадковим, але краще використовуйте команди:",
        "Гм, не спрацювало. Може спробуємо ці команди?",
        "Це повідомлення прекрасне, як веселка! Але для повноцінного спілкування спробуйте:",
        "Згідно з моїми розрахунками, це повідомлення не відповідає жодній з моїх команд. Ось вони:",
    ]
    random_response = choice(funny_responses)
    available_commands = """
    - Не знаєте, що обрати? Почніть з /start,
    - Спробуйте команду /gpt, щоб задати питання,
    """
    full_message = f"{random_response}\n{available_commands}"
    await update.message.reply_text(full_message)