from typing import List
from uuid import UUID

import psycopg
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_postgres import PostgresChatMessageHistory
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from dependencies.settings import get_settings

settings = get_settings()


class PostgresChatMessageHistoryLastNMessages(PostgresChatMessageHistory):
    def __init__(self, table_name: str, session_id: str, n: int, **kwargs):
        super().__init__(table_name, session_id, **kwargs)
        self.n = n

    def get_messages(self) -> List[BaseMessage]:
        messages = super().get_messages()
        return messages[-self.n:]


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    table_name = "chat_history"
    sync_connection = psycopg.connect(settings.SQLALCHEMY_DATABASE_URL)
    PostgresChatMessageHistory.create_tables(sync_connection, table_name)

    return PostgresChatMessageHistoryLastNMessages(
        table_name,
        session_id,
        sync_connection=sync_connection,
        n=10
    )


def get_chat_history(db: Session, feedback_id: UUID):
    history = db.execute(
        text('select c.message, c.created_at from chat_history c where c.session_id = :id order by c.created_at;'),
        {'id': feedback_id}
    ).all()

    history_dicts = [{'message': message, 'created_at': created_at} for message, created_at in history]

    return history_dicts
