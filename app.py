from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_client import query_llm
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Afaan Oromoo AI API")

# --- 1. ENABLE CORS ---
# This allows your frontend (index.html) to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. UPDATE DATA MODEL ---
# We add 'history' so the frontend can send the whole conversation back
class ChatRequest(BaseModel):
    user_input: str
    history: list = [] # Default to empty list if not provided

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Pass both input and history to your llm_client
    response = query_llm(request.user_input, request.history)
    
    return {
        "status": "success",
        "response": response
    }

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Ergaa: index.html hin argamne!</h1><p>Check if the file is in the same folder.</p>"
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)