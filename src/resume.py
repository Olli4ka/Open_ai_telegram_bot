import os
import logging
import collections

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update, InputFile
from telegram.ext import ContextTypes

from utils import send_image, send_text, load_prompt
from gpt import ChatGPTService
from config import CHATGPT_TOKEN

logger = logging.getLogger(__name__)


FONT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "fonts",
    "DejaVuSans.ttf"
)

pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))

chatgpt_service = ChatGPTService(CHATGPT_TOKEN)

RESUME_FIELDS = [
    ("specialty", "Напишіть вашу спеціальність:"),
    ("photo", "Надішліть фото (завантажте як зображення або файл):"),
    ("name", "Ваше ім'я:"),
    ("projects", "Найкращі проєкти (GitHub, якщо є):"),
    ("education", "Освіта:"),
    ("tech_skills", "Технічні скіли (через кому):"),
    ("soft_skills", "Софт скіли (максимум 4, через кому):"),
]

def resume_control_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔄 Почати знову", callback_data="resume_restart"),
                InlineKeyboardButton("🔙До головного меню", callback_data="start")
            ]
        ]
    )

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["conversation_state"] = "resume"

    await send_image(update, context, "resume")
    context.user_data["state"] = "resume"
    context.user_data["step_index"] = 0
    context.user_data["resume_data"] = {}
    await send_text(
        update,
        context,
        RESUME_FIELDS[0][1],
        reply_markup=resume_control_keyboard()
    )

async def message_handler_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "resume":
        return False

    step_index = context.user_data.get("step_index", 0)
    field_name, _ = RESUME_FIELDS[step_index]

    if field_name == "photo":
        if update.message.photo:
            file = update.message.photo[-1]
            file_obj = await file.get_file()

        elif update.message.document:
            file = update.message.document
            file_obj = await file.get_file()

        else:
            await send_text(
                update,
                context,
                "❗ Будь ласка, надішліть фото як зображення або файл."
            )
            return True

        os.makedirs("tmp", exist_ok=True)
        photo_path = f"tmp/{update.effective_user.id}_photo.jpg"
        await file_obj.download_to_drive(photo_path)

        context.user_data["resume_data"]["photo"] = photo_path

    else:
        context.user_data["resume_data"][field_name] = update.message.text

    step_index += 1

    if step_index < len(RESUME_FIELDS):
        context.user_data["step_index"] = step_index
        await send_text(
            update,
            context,
            RESUME_FIELDS[step_index][1],
            reply_markup=resume_control_keyboard()
        )
        return True

    await send_text(update, context, "⏳ Зачекайте, створюю резюме...")

    try:
        resume_text = await generate_resume_text(context.user_data["resume_data"])
        pdf_path = create_resume_pdf(
            context.user_data["resume_data"],
            resume_text,
            update.effective_user.id
        )
        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(
                InputFile(pdf_file, filename="resume.pdf")
            )
    except Exception as e:
        logger.exception("Ошибка при создании резюме")
        await send_text(update, context, "❌ Помилка при створенні резюме.")
    finally:
        context.user_data.clear()
    return True

async def generate_resume_text(data: dict) -> str:
    prompt_template = load_prompt("resume")
    safe_data = collections.defaultdict(str, data)
    filled_prompt = prompt_template.format_map(safe_data)
    chatgpt_service.set_prompt(filled_prompt)
    return await chatgpt_service.add_message(
        "Створи професійне резюме звичайним текстом, без Markdown, без ##, без списків та без символів форматування."
    )

def create_resume_pdf(data: dict, resume_text: str, user_id: int) -> str:
    os.makedirs("tmp", exist_ok=True)
    pdf_path = os.path.join("tmp", f"{user_id}_resume.pdf")

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("DejaVu", 20)
    c.drawString(
        50,
        y,
        f"{data.get('name', '')} — {data.get('specialty', '')}"
    )
    y -= 40

    if data.get("photo"):
        try:
            c.drawImage(
                data["photo"],
                400,
                height - 200,
                width=150,
                height=150,
                preserveAspectRatio=True,
                mask="auto"
            )
        except Exception as e:
            logger.error(f"Помилка під час додавання фото: {e}")

    c.setFont("DejaVu", 12)
    for line in resume_text.split("\n"):
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("DejaVu", 12)

        c.drawString(50, y, line)
        y -= 18

    c.save()
    return pdf_path

async def resume_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "resume_restart":
        context.user_data.clear()
        await resume(update, context)

    elif query.data == "resume_cancel":
        context.user_data.clear()
        await send_text(update, context, "❌ Створення резюме скасовано.")
