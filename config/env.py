from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LANGCHAIN_TRACING_V2: bool
    LANGCHAIN_API_KEY: str
    OPENAI_API_KEY: str
    SQLALCHEMY_DATABASE_URL: str
    GCP_PROJECT_ID: str
    PINECONE_API_KEY: str
    GEMINI_AI_KEY: str

    model_config = SettingsConfigDict(env_file=".env")
