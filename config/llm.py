from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic.v1 import BaseModel

from dependencies import get_settings

settings = get_settings()


class LLMProvider(BaseModel):
    model: BaseChatModel
    embedding: Any


open_ai = LLMProvider(
    model=ChatOpenAI(model="gpt-4o", temperature=0.2, api_key=settings.OPENAI_API_KEY),
    embedding=OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY),
)

google_vertex_ai = LLMProvider(
    model=ChatVertexAI(model="gemini-pro", temperature=0.2, convert_system_message_to_human=True,
                       project=settings.GCP_PROJECT_ID),
    embedding=VertexAIEmbeddings(model="text-multilingual-embedding-002", project=settings.GCP_PROJECT_ID),
)

current_provider = google_vertex_ai


def switch_provider_to(provider: LLMProvider):
    global current_provider
    current_provider = provider
