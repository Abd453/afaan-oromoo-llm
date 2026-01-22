import warnings
# Silence Google warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from llm_client import query_llm
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from database import get_database
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import os
import time
from typing import Optional, List

# ---------------- CONFIGURATION ----------------
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Afaan Oromoo AI API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize Database
db = get_database(os.getenv("DATABASE_PATH", "conversations.db"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# ---------------- DATA MODELS ----------------
class ChatRequest(BaseModel):
    user_input: str
    history: List[str] = []
    session_id: Optional[str] = None

    @field_validator("user_input")
    @classmethod
    def validate_input(cls, v):
        if not v or not v.strip():
            raise ValueError("Input cannot be empty")
        return v.strip()

class SessionCreate(BaseModel):
    session_id: str
    title: str

# ---------------- CHAT ENDPOINT (FIXED LANGUAGE) ----------------
@app.post("/chat")
@limiter.limit(os.getenv("RATE_LIMIT_PER_MINUTE", "30/minute"))
async def chat_endpoint(request: Request, payload: ChatRequest):
    try:
        start_time = time.time()

        # 1. FORCE AFAAN OROMOO
        # We inject a system command into the prompt here.
        # This ensures it speaks Afaan Oromoo even if you ask in English.
        forced_prompt = (
            "INSTRUCTION: You are a helpful AI assistant. "
            "You MUST answer ONLY in Afaan Oromoo. "
            "If the user inputs English, TRANSLATE your answer to Afaan Oromoo. "
            "Never reply in English.\n\n"
            f"User Question: {payload.user_input}"
        )

        # Query LLM
        response_text = query_llm(forced_prompt, payload.history)
        elapsed_time = time.time() - start_time

        # Save to Database
        if payload.session_id:
            try:
                db.add_message(payload.session_id, "user", payload.user_input)
                db.add_message(payload.session_id, "model", response_text)
                db.log_analytics(payload.session_id, response_time=elapsed_time, input_length=len(payload.user_input), output_length=len(response_text))
            except Exception as e:
                print(f"⚠️ DB Error: {e}")

        return {
            "status": "success",
            "response": response_text,
            "response_time": round(elapsed_time, 3)
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# ---------------- SESSION ENDPOINTS (FIXED IDs) ----------------
@app.post("/sessions")
async def create_session(session: SessionCreate):
    try:
        res = db.create_session(session.session_id, session.title)
        # FIX: Ensure we return 'session_id' correctly
        return {
            "status": "success", 
            "session": {
                "session_id": res.get('id', session.session_id), 
                "title": res['title']
            }
        }
    except Exception as e: raise HTTPException(500, str(e))

@app.get("/sessions")
async def list_sessions(limit: int = 50, offset: int = 0):
    try:
        raw_sessions = db.list_sessions(limit=limit, offset=offset)
        
        # CRITICAL FIX: Map 'id' (from DB) to 'session_id' (for Frontend)
        # This fixes the "Disappearing History" issue.
        formatted = []
        for s in raw_sessions:
            # Check for 'id' OR 'session_id' to be safe
            s_id = s.get("id") or s.get("session_id")
            if s_id:
                formatted.append({
                    "session_id": s_id, 
                    "title": s["title"], 
                    "created_at": s.get("created_at", "")
                })
                
        return {"status": "success", "sessions": formatted, "total": db.get_total_sessions()}
    except Exception as e: raise HTTPException(500, str(e))

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        session = db.get_session(session_id)
        if not session: raise HTTPException(404, "Session not found")
        
        raw_msgs = db.get_messages(session_id)
        # Format messages for UI
        formatted_msgs = [{"role": "bot" if m["role"] == "model" else "user", "parts": [m["content"]]} for m in raw_msgs]

        return {"status": "success", "session": session, "messages": formatted_msgs}
    except Exception as e: raise HTTPException(500, str(e))

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    try:
        # Validate ID isn't 'undefined'
        if session_id == "undefined" or not session_id: 
            raise HTTPException(400, "Invalid Session ID")
            
        deleted = db.delete_session(session_id)
        if not deleted: raise HTTPException(404, "Session not found")
        return {"status": "success"}
    except Exception as e: raise HTTPException(500, str(e))

# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
async def home():
    if os.path.exists("index.html"): return FileResponse("index.html")
    return "<h1>Error: index.html not found</h1>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)