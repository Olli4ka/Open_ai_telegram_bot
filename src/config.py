import os
from dotenv import load_dotenv

load_dotenv()

CHATGPT_TOKEN = os.getenv("CHATGPT_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")