from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from handlers import (
    start,
    random,
    random_button,
    gpt,
    talk,
    talk_button,
    message_handler,
)
from translator import translator, translator_button, handle_translation


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("random", random))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("talk", talk))
app.add_handler(CommandHandler("translator", lambda update, context: translator(update, context, start_func=start)))

app.add_handler(
    CallbackQueryHandler(
        lambda update, context: translator_button(update, context, start_func=start),
        pattern="^(translate_en|translate_uk|translate_de|translator|start)$"
    )
)

app.add_handler(
    CallbackQueryHandler(
        talk_button,
        pattern="^(talk_linus_torvalds|talk_guido_van_rossum|talk_mark_zuckerberg|start)$"
    )
)

app.add_handler(
    CallbackQueryHandler(
        random_button,
        pattern="^(random|start)$"
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler
    )
)

app.run_polling(
    drop_pending_updates=True,
    allowed_updates=Update.ALL_TYPES
)

