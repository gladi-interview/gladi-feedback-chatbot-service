from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies.db import get_db
from models import FeedbackCreate, FeedbackQuestion
from services.video_feedback import create_feedback, get_feedback, ask_feedback

router = APIRouter(
    prefix="/video-feedbacks",
    tags=["video_feedbacks"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
def create_video_feedback(dto: FeedbackCreate, db: Session = Depends(get_db)):
    return create_feedback(dto, db)


@router.get("/{feedback_id}")
def get_video_feedback(feedback_id: UUID, db: Session = Depends(get_db)):
    feedback = get_feedback(feedback_id, db)

    if feedback is None:
        raise HTTPException(status_code=404, detail="User not found")

    return feedback


@router.patch("/{feedback_id}")
def ask_video_feedback(feedback_id: UUID, dto: FeedbackQuestion, db: Session = Depends(get_db)):
    feedback = get_feedback(feedback_id, db)

    if feedback is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not feedback.content_is_matched_with_context:
        raise HTTPException(status_code=422, detail='Presentation content is not matched with context')

    return {
        "question": dto.question,
        "answer": ask_feedback(feedback, dto)
    }
