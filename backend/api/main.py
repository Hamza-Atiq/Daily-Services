"""
FastAPI server integrating Google ADK agents with REST endpoints.
Serves as the backend for the Flutter mobile app.
"""

import os
import sys
import json
import uuid
import asyncio
import logging
import traceback
from datetime import datetime
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("api")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from service_orchestrator.agent import root_agent


# ── Session management ───────────────────────────────────────────────────────
session_service = InMemorySessionService()
APP_NAME = "service_orchestrator"

# Store traces for each request
trace_store: dict = {}


# ── Pydantic models ──────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    user_id: str = "default_user"


class ChatResponse(BaseModel):
    session_id: str
    response: str
    trace: list | None = None
    timestamp: str


class DisputeRequest(BaseModel):
    booking_id: str
    complaint: str
    session_id: str | None = None


# ── App lifecycle ────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed Firebase if needed
    try:
        from api.core.firebase import get_db
        from service_orchestrator.data.seed_firebase import seed_providers
        db = get_db()
        seed_providers(db)
        print("[OK] Firebase connected and data seeded")
    except Exception as e:
        print(f"[WARN] Firebase not connected (using local fallback): {e}")
    
    print("[START] Service Orchestrator API is running!")
    print(f"[API] Endpoints: /chat, /bookings, /providers, /trace/{{request_id}}")
    yield
    print("[STOP] Shutting down...")


# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Service Orchestrator API",
    description="Agentic AI system for Pakistan's informal economy service matching",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper: run agent ────────────────────────────────────────────────────────
async def run_agent(session_id: str, user_id: str, message: str) -> tuple[str, list]:
    """Run the root agent with a user message and return response + trace."""
    
    # Ensure session exists
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)],
    )

    trace_steps = []
    final_response = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_content,
    ):
        # Collect trace events
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    if hasattr(event, 'author') and event.author != "user":
                        final_response = part.text
                
                if hasattr(part, 'function_call') and part.function_call:
                    trace_steps.append({
                        "type": "tool_call",
                        "agent": getattr(event, 'author', 'unknown'),
                        "tool": part.function_call.name,
                        "args": dict(part.function_call.args) if part.function_call.args else {},
                        "timestamp": datetime.now().isoformat(),
                    })
                
                if hasattr(part, 'function_response') and part.function_response:
                    trace_steps.append({
                        "type": "tool_response",
                        "agent": getattr(event, 'author', 'unknown'),
                        "tool": part.function_response.name,
                        "timestamp": datetime.now().isoformat(),
                    })

    return final_response, trace_steps


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Service Orchestrator",
        "version": "1.0.0",
        "agents": [
            "service_orchestrator (root)",
            "intent_parser",
            "ac_repair_specialist",
            "plumbing_specialist",
            "electrical_specialist",
            "cleaning_specialist",
            "booking_manager",
            "followup_manager",
            "dispute_handler",
        ],
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint. Send a user message and get an AI agent response."""
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        response_text, trace = await run_agent(
            session_id=session_id,
            user_id=request.user_id,
            message=request.message,
        )

        # Store trace
        request_id = str(uuid.uuid4())[:8]
        trace_store[request_id] = {
            "request_id": request_id,
            "session_id": session_id,
            "user_message": request.message,
            "response": response_text,
            "trace": trace,
            "timestamp": datetime.now().isoformat(),
        }

        return ChatResponse(
            session_id=session_id,
            response=response_text or "I'm processing your request. Please try again.",
            trace=trace,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error("Agent error on /chat: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Agent error: {type(e).__name__}: {e}")


@app.post("/dispute")
async def create_dispute(request: DisputeRequest):
    """Submit a dispute for a booking."""
    session_id = request.session_id or str(uuid.uuid4())
    
    dispute_message = f"I have a complaint about booking {request.booking_id}: {request.complaint}"
    
    response_text, trace = await run_agent(
        session_id=session_id,
        user_id="dispute_user",
        message=dispute_message,
    )

    return {
        "session_id": session_id,
        "response": response_text,
        "trace": trace,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/bookings")
async def list_bookings():
    """Get all bookings."""
    from service_orchestrator.tools.booking_tools import get_all_bookings
    return get_all_bookings()


@app.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """Get a specific booking."""
    from service_orchestrator.tools.booking_tools import get_booking_by_id
    result = get_booking_by_id(booking_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@app.get("/providers")
async def list_providers():
    """Get all registered providers."""
    from service_orchestrator.tools.provider_tools import _load_providers
    providers = _load_providers()
    return {"total": len(providers), "providers": providers}


@app.get("/trace/{request_id}")
async def get_trace(request_id: str):
    """Get agent trace for a specific request."""
    if request_id not in trace_store:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace_store[request_id]


@app.get("/traces")
async def list_traces():
    """Get all stored agent traces."""
    return {
        "total": len(trace_store),
        "traces": list(trace_store.values()),
    }


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("api.main:app", host=host, port=port, reload=True)
