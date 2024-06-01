from config import Base
from sqlalchemy import Column, Integer, Boolean


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True)
    content_is_matched_with_context = Column(Boolean)
