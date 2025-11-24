from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import build_qa

app = FastAPI()
qa = build_qa()

class Question(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(q: Question):
    global qa
    if qa is None:
        return {"answer": "El sistema aún se está inicializando."}

    response = qa.invoke(q.question)

    return {
        "answer": response.content
    }
