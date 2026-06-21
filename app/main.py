from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import os
import json

# Load env
load_dotenv()

from rag import init_rag, get_documents_count
from agent import app_agent, extract_json
from langchain_core.messages import HumanMessage
from tools import calculate_pemdi_index as tool_calculate_index

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG Agent Pemdi", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

class Source(BaseModel):
    page: Optional[int] = None
    content: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    session_id: str

class CalculateRequest(BaseModel):
    indicators: Dict[str, float]

class CalculateResponse(BaseModel):
    indeks_pemdi: float
    predikat: str
    detail_aspek: Dict[str, float]

@app.on_event("startup")
async def startup_event():
    print("Starting up RAG Agent service...")
    try:
        init_rag()
    except Exception as e:
        print(f"Error initializing RAG: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        # Invoke LangGraph
        result = app_agent.invoke(inputs)
        
        last_message = result["messages"][-1]
        try:
            parsed = extract_json(last_message.content)
            answer = parsed.get("final_answer") or last_message.content
        except:
            answer = last_message.content
        
        # Extract sources from the search_pemdi_doc tool responses
        sources = []
        for msg in result["messages"]:
            if isinstance(msg, HumanMessage) and "Observation for search_pemdi_doc:" in msg.content:
                # Splitting the formatted string back to list of dicts for API response
                chunks = msg.content.split("\n\n---\n\n")
                for chunk in chunks:
                    if "[Halaman " in chunk:
                        try:
                            # Extract page
                            page_str = chunk.split("[Halaman ")[1].split("]")[0]
                            page = int(page_str)
                            content = chunk.split("]\n")[1]
                            sources.append(Source(page=page, content=content[:200] + "..."))
                        except:
                            sources.append(Source(content=chunk[:200] + "..."))
                            
        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=request.session_id
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate-index", response_model=CalculateResponse)
async def calculate_index(request: CalculateRequest):
    try:
        # Call the tool function directly
        result = tool_calculate_index.invoke({"indicators": request.indicators})
        return CalculateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    doc_count = get_documents_count()
    return {
        "status": "ok",
        "vector_db": "ready" if doc_count > 0 else "empty",
        "documents_indexed": doc_count
    }

from fastapi.staticfiles import StaticFiles
import os

# Create static dir if it doesn't exist to prevent crash before frontend is built
if not os.path.exists("static"):
    os.makedirs("static")

# Mount static files at root
app.mount("/", StaticFiles(directory="static", html=True), name="static")
