from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_client import query_llm
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import os

app = FastAPI(title="Afaan Oromoo AI API")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODEL ---
class ChatRequest(BaseModel):
    user_input: str
    history: list = [] 

# --- ENDPOINTS ---
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Pass history so the AI has context
    response_text = query_llm(request.user_input, request.history)
    
    return {
        "status": "success",
        "response": response_text
    }

@app.get("/", response_class=HTMLResponse)
async def home():
    # Helper to find index.html even if run from different folder
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return "<h1>Error: index.html not found</h1>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)