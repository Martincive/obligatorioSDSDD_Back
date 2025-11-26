from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import build_qa
from sse_starlette.sse import EventSourceResponse
import asyncio

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

        async for chunk in qa.astream(q.question):

            text = chunk.content

            if not text:
                continue

            yield {
                "event": "message",
                "data": text,
            }

            await asyncio.sleep(0)

        yield {
            "event": "done",
            "data": "end"
        }


    return EventSourceResponse(event_generator())
