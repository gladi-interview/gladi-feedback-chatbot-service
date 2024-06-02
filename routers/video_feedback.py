from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.db import get_db
from models import FeedbackCreate
from services.video_feedback import create_feedback

router = APIRouter(
    prefix="/video-feedbacks",
    tags=["video_feedbacks"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
def create_video_feedback(dto: FeedbackCreate, db: Session = Depends(get_db)):
    return create_feedback(dto, db)


@router.get("/{video_id}")
def get_video_feedback(video_id: UUID):
    return {"video_id": video_id, "message": "Video feedback retrieved successfully"}


@router.put("/{video_id}")
def ask_video_feedback(video_id: UUID):
    return {"video_id": video_id, "message": "Video feedback asked successfully"}
