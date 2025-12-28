# Telegram ChatGPT Bot
A versatile Telegram bot that integrates with OpenAI's ChatGPT to provide various interactive features.

![start.png](src/resources/images/start.png)

---

### ✔ Core Features:

- **Random Fact Generator** - Get interesting facts with AI-generated content
- **ChatGPT Interface** - Direct chat with OpenAI's ChatGPT
- **Celebrity Chat** - Chat with AI personalities
- **Language Translator** - Interactive AI translator with language switching
- **Resume Assistant** - By using GPT step-by-step resume builder with photo upload and PDF export

---

![random.jpeg](src/resources/images/random.jpeg)

### ✔ Prerequisites

- Python 3.8+
- Telegram Bot Token
- OpenAI API Key
- Required Python packages (see `requirements.txt`)

---

### ✔ Installation

Clone the repository:

```
git clone <repository-url>
cd Open_ai_telegram_bot
```

Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```
Create a `.env` file in the project root and add your tokens:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

---

### ✔ Usage

Start the bot:

```bash
python src/bot.py
```

In Telegram, find your bot using the username you set up and start a chat.

Available commands:

- `/start` - Start the bot
- `/random` - Get a random fact
- `/gpt` - Chat with ChatGPT
- `/talk` - Chat with a celebrity personality
- `/translator` - Translate words
- `/resume` - Create resume

![gpt.jpg](src/resources/images/gpt.jpg)

---

### ✔ Project Structure

```
open_ai_telegram_bot
├── .env.example                             # Example environment variables
├── .gitignore                               # Git ignore file
├── README.md                                # This file
├── requirements.txt                         # Project dependencies
└── src/
    ├── bot.py                               # Main bot application
    ├── config.py                            # Configuration settings
    ├── gpt.py                               # GPT integration module
    ├── handlers.py                          # Bot command handlers
    ├── utils.py                             # Utility functions
    ├── translator.py                        # Language translator module
    ├── resume.py                            # Resume builder module
    ├── talk.py                              # Celebrity chat module
    ├── resources/                           # Resource files
    │    ├── images/                         # Image assets for the bot
    │    ├── messages/                       # Message templates
    │    │   └── start.txt
    │    └── prompts/                        # AI prompt templates
    │        ├── gpt.txt
    │        ├── random.txt
    │        ├── resume.txt
    │        ├── translator/
    │        │   ├── en.txt
    │        │   ├── de.txt
    │        │   └── uk.txt
    │        ├── talk_guido_van_rossum.txt
    │        ├── talk_linus_torvalds.txt
    │        └── talk_mark_zuckerberg.txt
    ├── fonts/                               # Custom fonts for PDF generation
    └── tmp/                                 # Temporary files (generated PDFs, uploaded photos)
```

---

### ✔ Environment Variables

The following environment variables need to be set:

- `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token from @BotFather
- `OPENAI_API_KEY`: Your OpenAI API key

![translator.png](src/resources/images/translator.png)

---

### ✔ Contributing

- Fork the repository
- Create a new branch for your feature
- Commit your changes
- Push to the branch
- Create a new Pull Request

---

### ✔ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

![resume.png](src/resources/images/resume.png)

---