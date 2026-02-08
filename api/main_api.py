# api/main_api.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.brain import get_answer

app = FastAPI()

# Permitem accesul din browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask_ai(q: Question):
    answer = get_answer(q.question)
    return {"answer": answer}
