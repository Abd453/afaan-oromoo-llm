from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
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

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Afaan Oromoo AI API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize database
db = get_database(os.getenv("DATABASE_PATH", "conversations.db"))

# --- CORS ---
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

# --- DATA MODELS ---
class ChatRequest(BaseModel):
    user_input: str
    history: list = []
    session_id: Optional[str] = None
    
    @validator('user_input')
    def validate_input(cls, v):
        if not v or not v.strip():
            raise ValueError("Input cannot be empty")
        if len(v) > 2000:
            raise ValueError("Input too long (max 2000 characters)")
        return v.strip()

class SessionCreate(BaseModel):
    session_id: str
    title: str

class SessionUpdate(BaseModel):
    title: str

# --- CHAT ENDPOINT ---
@app.post("/chat")
@limiter.limit(os.getenv("RATE_LIMIT_PER_MINUTE", "30/minute"))
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint with database persistence and analytics.
    """
    try:
        start_time = time.time()
        
        # Query LLM
        response_text = query_llm(request.user_input, request.history)
        
        elapsed_time = time.time() - start_time
        
        # Save to database if session_id provided
        if request.session_id:
            try:
                # Save user message
                db.add_message(
                    session_id=request.session_id,
                    role="user",
                    content=request.user_input,
                    token_count=len(request.user_input.split())
                )
                
                # Save assistant response
                db.add_message(
                    session_id=request.session_id,
                    role="model",
                    content=response_text,
                    token_count=len(response_text.split())
                )
                
                # Log analytics
                db.log_analytics(
                    session_id=request.session_id,
                    response_time=elapsed_time,
                    input_length=len(request.user_input),
                    output_length=len(response_text)
                )
            except Exception as db_error:
                # Don't fail the request if database fails
                print(f"Database error: {db_error}")
        
        return {
            "status": "success",
            "response": response_text,
            "response_time": round(elapsed_time, 3)
        }
    
    except ValueError as e:
        db.log_analytics(error=str(e), input_length=len(request.user_input))
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        db.log_analytics(error=str(e), input_length=len(request.user_input))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Rakkoo teeknikaa uumame. Maaloo irra deebi'ii yaalaa.",
                "error": str(e)
            }
        )

# --- SESSION MANAGEMENT ENDPOINTS ---
@app.post("/sessions")
async def create_session(session: SessionCreate):
    """Create a new conversation session."""
    try:
        result = db.create_session(session.session_id, session.title)
        return {"status": "success", "session": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions(limit: int = 50, offset: int = 0):
    """List all conversation sessions."""
    try:
        sessions = db.list_sessions(limit=limit, offset=offset)
        return {
            "status": "success",
            "sessions": sessions,
            "total": db.get_total_sessions()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session with its messages."""
    try:
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = db.get_messages(session_id)
        
        return {
            "status": "success",
            "session": session,
            "messages": messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/sessions/{session_id}")
async def update_session(session_id: str, update: SessionUpdate):
    """Update session title."""
    try:
        db.update_session(session_id, title=update.title)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its messages."""
    try:
        deleted = db.delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ANALYTICS ENDPOINT ---
@app.get("/analytics")
async def get_analytics(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get usage analytics."""
    try:
        summary = db.get_analytics_summary(start_date, end_date)
        errors = db.get_error_logs(limit=20)
        
        return {
            "status": "success",
            "summary": summary,
            "recent_errors": errors,
            "total_sessions": db.get_total_sessions(),
            "total_messages": db.get_total_messages()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def home():
    # Helper to find index.html even if run from different folder
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return "<h1>Error: index.html not found</h1>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)