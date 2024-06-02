from fastapi import FastAPI
from config import engine
from models import Base
from routers import video_feedback

Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api")
app.include_router(video_feedback.router)


@app.get("/")
async def root():
    return {"message": "Hello Feedback Chatbot"}
