from models import model
from sqlalchemy.orm import Session, joinedload
from uuid import UUID


def create_feedback_analysis(db: Session, feedback_id, index_name, response_answer, isMatch):
    feedback = model.Feedback(
        id=feedback_id,
        content_is_matched_with_context=isMatch,
        index_name=index_name,
    )
    analysis_result = model.Analysis(
        feedback_id=feedback.id,
        goods=response_answer.goods,
        bads=response_answer.bads,
        corrections=response_answer.corrections,
        suggestions=response_answer.suggestions,
        overall_feedback=response_answer.feedback,
    )
    db.add(feedback)
    db.add(analysis_result)
    db.commit()
    db.refresh(analysis_result)
    db.refresh(feedback)

    return analysis_result, feedback


def get_feedback_model(db: Session, feedback_id: UUID):
    return db.query(model.Feedback).options(
        joinedload(model.Feedback.analysis)
    ).where(model.Feedback.id == feedback_id).first()
