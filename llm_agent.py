import uuid
from typing import Sequence

from dotenv import find_dotenv, load_dotenv
from langchain_core.language_models import LanguageModelLike
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool
from langchain_gigachat.chat_models import GigaChat
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from os import getenv

load_dotenv(find_dotenv())

DOCUMENT_FILE = "Документ с ответами.docx"  # путь к файлу с содержанием


@tool
def answer_from_file(question: str) -> str:
    """
    Отвечает на вопрос пользователя на основе содержимого загруженного файла.

    Args:
        question (str): Вопрос пользователя

    Returns:
        str: Ответ, найденный в документе
    """
    return f"Ответ на вопрос «{question}» содержится в прикреплённом файле. Используй его содержимое, чтобы ответить."  # На самом деле, логика будет использоваться внутри агента


class LLMAgent:
    def __init__(self, model: LanguageModelLike, tools: Sequence[BaseTool]):
        self._model = model
        self._agent = create_react_agent(
            model, tools=tools, checkpointer=InMemorySaver()
        )
        self._config: RunnableConfig = {"configurable": {"thread_id": uuid.uuid4().hex}}

    def upload_file(self, file):
        file_uploaded_id = self._model.upload_file(file).id_  # type: ignore
        return file_uploaded_id

    def invoke(
        self,
        content: str,
        attachments: list[str] | None = None,
        temperature: float = 0.1,
    ) -> str:
        message: dict = {
            "role": "user",
            "content": content,
            **({"attachments": attachments} if attachments else {}),
        }
        return self._agent.invoke(
            {"messages": [message], "temperature": temperature}, config=self._config
        )["messages"][-1].content


def print_agent_response(llm_response: str) -> None:
    print(f"\033[36m{llm_response}\033[0m")


def get_user_prompt() -> str:
    return input("\nТы: ")


def setup():
    model = GigaChat(
        credentials=getenv("GIGACHAT_CREDENTIALS"),
        model="GigaChat-2-Max",
        verify_ssl_certs=False,
    )

    agent = LLMAgent(model, tools=[answer_from_file])

    system_prompt = (
        "Ты помощник, который отвечает на вопросы пользователя на основе прикреплённого документа. "
        "Если в документе нет точного ответа — честно скажи об этом. Не выдумывай. "
        "Используй содержимое документа, чтобы дать максимально точный и полный ответ. "
        "Пожалуйста, задай вопрос, по которому ты хочешь получить ответ из документа."
    )

    file_uploaded_id = agent.upload_file(open(DOCUMENT_FILE, "rb"))
    agent_response = agent.invoke(content=system_prompt, attachments=[file_uploaded_id])
    return agent, agent_response


def main():
    agent, agent_response = setup()
    while True:
        print_agent_response(agent_response)
        agent_response = agent.invoke(get_user_prompt())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nДо свидания!")
