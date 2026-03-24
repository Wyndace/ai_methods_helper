# ai_methods_helper

Telegram-бот + LLM-агент для помощи с экзаменом по философии.

Загружает PDF-материалы (вопросы и подробные ответы), отвечает на вопросы пользователя через LLM с контекстом из документов.

## Стек

- Python 3 (python-telegram-bot)
- LLM-агент (llm_agent.py)
- uv

## Запуск

```bash
uv sync
uv run telegram-bot.py
```
