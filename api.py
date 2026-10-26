import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from main import run_pipeline
from core.rag_engine import ask_question, load_rag_chain

load_dotenv()

app = FastAPI(
    title="AI Video Assistant API",
    description="Backend API for transcribing videos, generating summaries, extracting action items, and conversational RAG chat.",
    version="1.0.0",
)

# Enable CORS for local frontends (React, Vue, Streamlit, etc.)
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
        example="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )
    language: Optional[str] = Field(
        "english",
        description="Transcription language: 'english' or 'hinglish'",
    )


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        description="Question to ask about the processed meeting transcript",
        example="What were the main action items discussed?",
    )


@app.get("/")
def root():
    """Welcome endpoint providing server status and documentation links."""
    return {
        "status": "online",
        "message": "AI Video Assistant API is running successfully!",
        "endpoints": {
            "docs": "http://127.0.0.1:8000/docs",
            "redoc": "http://127.0.0.1:8000/redoc",
            "process_video": "POST http://127.0.0.1:8000/process",
            "chat": "POST http://127.0.0.1:8000/chat",
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
            rag_chain = load_rag_chain()
            current_session["rag_chain"] = rag_chain
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="No meeting transcript found. Please process a video first via POST /process.",
            )

    try:
        answer = ask_question(rag_chain, request.question)
        return {
            "question": request.question,
            "answer": answer,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    print("=" * 70)
    print("🚀 Starting FastAPI Server...")
    print(f"🌐 Localhost Server Link: http://{host}:{port}")
    print(f"📖 Interactive Swagger Docs: http://{host}:{port}/docs")
    print(f"📚 ReDoc Documentation:    http://{host}:{port}/redoc")
    print("=" * 70)
    uvicorn.run("api:app", host=host, port=port, reload=True)
