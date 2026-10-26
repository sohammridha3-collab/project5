import os
import socket
import sys
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

load_dotenv()

app = FastAPI(
    title="AI Video Assistant API",
    description="Backend REST API for transcribing videos, generating summaries, extracting action items, and conversational RAG chat.",
    version="1.0.0",
)

# Enable CORS for frontend clients (React, Vue, Streamlit, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active session RAG chain and last result
current_session = {
    "rag_chain": None,
    "last_result": None,
}


class ProcessVideoRequest(BaseModel):
    source: str = Field(
        ...,
        description="YouTube URL or local path to audio/video file",
        json_schema_extra={"example": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
    )
    language: Optional[str] = Field(
        "english",
        description="Transcription language: 'english' or 'hinglish'",
    )


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        description="Question to ask about the processed meeting transcript",
        json_schema_extra={"example": "What were the main action items discussed?"},
    )


@app.get("/")
def root():
    """Welcome endpoint providing server status and documentation links."""
    return {
        "status": "online",
        "message": "AI Video Assistant API is running successfully!",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
        "endpoints": {
            "process_video": "POST /process",
            "chat": "POST /chat",
            "health": "GET /health",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/process")
def process_video(request: ProcessVideoRequest):
    """
    Process a video or audio input:
    1. Downloads & extracts audio
    2. Transcribes with Whisper or Sarvam
    3. Generates title and summary
    4. Extracts action items, decisions, and questions
    5. Builds the Chroma vector database and RAG chain
    """
    try:
        from main import run_pipeline
        result = run_pipeline(source=request.source, language=request.language or "english")

        # Save rag_chain in memory for chat queries
        current_session["rag_chain"] = result.get("rag_chain")
        current_session["last_result"] = {
            "title": result.get("title"),
            "summary": result.get("summary"),
            "action_items": result.get("action_items"),
            "key_decisions": result.get("key_decisions"),
            "open_questions": result.get("open_questions"),
            "transcript_preview": result.get("transcript", "")[:300],
        }

        return {
            "status": "success",
            "data": current_session["last_result"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat_with_meeting(request: ChatRequest):
    """
    Chat with the processed meeting using RAG.
    Requires a video to have been processed first, or an existing vector DB.
    """
    rag_chain = current_session.get("rag_chain")
    if not rag_chain:
        try:
            from core.rag_engine import load_rag_chain
            rag_chain = load_rag_chain()
            current_session["rag_chain"] = rag_chain
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="No meeting transcript found. Please process a video first via POST /process.",
            )

    try:
        from core.rag_engine import ask_question
        answer = ask_question(rag_chain, request.question)
        return {
            "question": request.question,
            "answer": answer,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def find_available_port(preferred_port: int = 8000) -> int:
    """Finds an available TCP port starting from the preferred port."""
    for port in [preferred_port, 8001, 8080, 8081, 5000]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            # connect_ex != 0 means port is free to bind
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return preferred_port


if __name__ == "__main__":
    host = "127.0.0.1"
    port = find_available_port(preferred_port=8000)

    print("\n" + "=" * 65)
    print(" 🚀 FastAPI Server is Starting...")
    print(f" 🌐 Running Server URL:     http://{host}:{port}")
    print(f" 📖 Interactive Swagger UI: http://{host}:{port}/docs")
    print(f" 📚 Alternative ReDoc Docs: http://{host}:{port}/redoc")
    print("=" * 65 + "\n")

    uvicorn.run("api:app", host=host, port=port, reload=True)
