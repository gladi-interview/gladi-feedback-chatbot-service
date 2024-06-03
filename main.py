from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_postgres import PostgresChatMessageHistory

from config import engine
from dependencies.settings import get_settings
from models import Base
from routers import video_feedback


@asynccontextmanager
async def lifespan():
    setup_database()


cors_allowed_origin = [
    "https://gladi.netlify.app",
    "https://gladiprocessing.anickme.com"
]

app = FastAPI(root_path="/api")
app.include_router(video_feedback.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
