import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from llm_agent import setup

# Загружаем агента из готового llm_agent.py
agent, _ = setup()  # system_prompt можно не выводить пользователю в Telegram


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        response = agent.invoke(user_input)
    except Exception as e:
        logging.exception("Ошибка при обработке запроса LLM:")
        response = "Произошла ошибка при получении ответа. Попробуйте позже."
    await update.message.reply_text(response)


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
