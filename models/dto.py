from pydantic import BaseModel, AnyHttpUrl


class FeedbackCreate(BaseModel):
    transcript: str
    context_url: AnyHttpUrl
