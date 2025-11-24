from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import build_qa
from sse_starlette.sse import EventSourceResponse

app = FastAPI()
qa = build_qa()

class Question(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat/stream")
async def chat_stream(q: Question):

    async def event_generator():
        for chunk in qa.stream(q.question):
            yield {"data": chunk.content}

    return EventSourceResponse(event_generator())
