import psycopg
from fastapi import FastAPI
from langchain_postgres import PostgresChatMessageHistory

from config import engine
from dependencies.settings import get_settings
from models import Base
from routers import video_feedback

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()


app = FastAPI(root_path="/api")
app.include_router(video_feedback.router)


@app.get("/")
async def root():
    return {"message": "Hello Feedback Chatbot"}


def setup_database():
    settings = get_settings()

    table_name = "chat_history"
    sync_connection = psycopg.connect(settings.SQLALCHEMY_DATABASE_URL)
    PostgresChatMessageHistory.create_tables(sync_connection, table_name)
    Base.metadata.create_all(bind=engine)
    sync_connection.close()
