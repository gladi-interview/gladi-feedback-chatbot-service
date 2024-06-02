from uuid import uuid4

from sqlalchemy import Column, Boolean, UUID, ARRAY, String, ForeignKey
from sqlalchemy.orm import relationship

from config import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(UUID, primary_key=True, default=uuid4)
    content_is_matched_with_context = Column(Boolean, default=True)
    index_name = Column(String)

    analysis = relationship("Analysis", uselist=False)


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(UUID, primary_key=True, default=uuid4)
    goods = Column(ARRAY(String))
    bads = Column(ARRAY(String))
    corrections = Column(ARRAY(String))
    suggestions = Column(ARRAY(String))
    overall_feedback = Column(String)

    feedback_id = Column(UUID, ForeignKey("feedbacks.id"))
    feedback = relationship("Feedback", uselist=False)
