from fastapi import FastAPI
from config import engine
from models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Feedback Chatbot"}
