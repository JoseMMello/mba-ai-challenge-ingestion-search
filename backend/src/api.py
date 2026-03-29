import json
import os
from typing import Callable, Generator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from search import search_prompt, search_prompt_stream

load_dotenv()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app = FastAPI(title="RAG Chat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


chain: Callable[[str], str] | None = None
chain_stream: Callable[[str], Generator[str, None, None]] | None = None


def _ensure_chains() -> None:
    global chain, chain_stream

    if chain is None:
        chain = search_prompt()
    if chain_stream is None:
        chain_stream = search_prompt_stream()

    if chain is None or chain_stream is None:
        raise RuntimeError(
            "Falha ao inicializar RAG. Verifique DATABASE_URL, OPENAI_API_KEY e se o banco está no ar."
        )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
def chat(payload: ChatRequest) -> dict:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem vazia")

    try:
        _ensure_chains()
        assert chain is not None
        answer = chain(payload.message)
        return {"answer": answer}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar chat: {e}") from e


@app.post("/chat/stream")
def chat_stream(payload: ChatRequest) -> StreamingResponse:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem vazia")

    try:
        _ensure_chains()
        assert chain_stream is not None
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    def event_generator() -> Generator[str, None, None]:
        try:
            for token in chain_stream(payload.message):
                data = json.dumps({"token": token}, ensure_ascii=False)
                yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"event: error\ndata: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
