"""
IdeaForge Backend — FastAPI + HuggingFace Transformers
Multi-Agent AI Ideation Platform — Fully Local, No External AI APIs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import logging

from agents import AGENTS
from orchestrator import DiscussionOrchestrator
from model_manager import ModelManager

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="IdeaForge API",
    description="Multi-Agent AI Ideation Platform — Fully Local HuggingFace Transformers",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global model manager (loads once, reused) ─────────────────────────────────
model_manager = ModelManager()

# ── Schemas ───────────────────────────────────────────────────────────────────
class DiscussionRequest(BaseModel):
    thread: str
    rounds: Optional[int] = 2
    selected_agents: Optional[list[str]] = None  # None = all agents

class LoadModelRequest(BaseModel):
    model_name: str = "google/flan-t5-base"

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "IdeaForge API is running", "status": "ok", "version": "2.0.0"}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": model_manager.is_loaded(),
        "model_name": model_manager.model_name,
        "device": model_manager.device
    }


@app.post("/api/load-model")
async def load_model(model_name: str = "google/flan-t5-base"):
    """
    Load (or reload) a HuggingFace model into memory.
    If a model is already loaded, it will be unloaded first to free RAM.
    Query param: model_name (str)
    """
    try:
        logger.info(f"Request to load model: {model_name}")

        # Run the blocking model load in a thread so we don't block the event loop
        await asyncio.to_thread(model_manager.load, model_name)

        return {
            "status": "loaded",
            "model": model_manager.model_name,
            "device": model_manager.device
        }
    except Exception as e:
        logger.error(f"Model load failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/unload-model")
async def unload_model():
    """Unload the current model to free RAM."""
    model_manager.unload()
    return {"status": "unloaded"}


@app.get("/api/agents")
async def get_agents():
    """Return all agent definitions."""
    return {"agents": [
        {
            "id": a["id"],
            "name": a["name"],
            "role": a["role"],
            "color": a["color"],
            "avatar": a["avatar"],
            "personality": a["personality"]
        } for a in AGENTS
    ]}


@app.post("/api/discuss")
async def discuss(request: DiscussionRequest):
    """
    Run a multi-agent discussion via Server-Sent Events streaming.
    Each agent speaks in sequence, per round, then a final synthesis is generated.
    """
    if not model_manager.is_loaded():
        raise HTTPException(
            status_code=400,
            detail="Model not loaded. Please load a model first via the model panel."
        )

    if not request.thread.strip():
        raise HTTPException(status_code=400, detail="Thread cannot be empty.")

    orchestrator = DiscussionOrchestrator(
        model_manager=model_manager,
        thread=request.thread,
        rounds=min(max(request.rounds, 1), 3),  # clamp 1-3 rounds
        selected_agents=request.selected_agents
    )

    async def event_stream():
        async for event in orchestrator.run():
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0)
        yield 'data: {"type": "stream_end"}\n\n'

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )
