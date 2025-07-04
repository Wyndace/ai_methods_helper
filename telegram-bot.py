import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from llm_agent import setup
import re

# Загружаем агента из готового llm_agent.py
agent, _ = setup()  # system_prompt можно не выводить пользователю в Telegram


def escape_markdown_v2(text: str) -> str:
    return re.sub(r"([\-_\*\[\]\(\)~`>#+=|{}.!])", r"\\\1", text)


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if message := update.message:
        user_input = message.text
        try:
            await context.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            if user_input:
                response = agent.invoke(user_input)
            else:
                raise ValueError("Пустой ввод пользователя")
        except Exception as e:
            logging.exception("Ошибка при обработке запроса LLM:")
            response = f"Произошла ошибка при получении ответа. Попробуйте позже.\n {e.__str__()}"
        await message.reply_text(escape_markdown_v2(response), parse_mode="MarkdownV2")


def main():
    from dotenv import load_dotenv, find_dotenv
    import os

    load_dotenv(find_dotenv())
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не задан в .env")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram-бот запущен и ждёт вопросов.")
    app.run_polling()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
