from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import uuid

from app.config import settings
from app.embeddings import init_embedding_service, get_embedding_service
from app.agent import init_agent, get_agent  # Imports from app/agent/__init__.py
from app.knowledge_base import knowledge_base
from app.session import session_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== DATA MODELS ==========

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Session ID, generated if not provided")
    user_id: Optional[str] = Field("anonymous", description="User identifier")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    session_id: str
    user_id: str
    answer: str
    route: str  # kb, ai, error
    confidence: str  # high, medium, low
    is_new_session: bool
    message_count: int
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    embeddings_ready: bool
    agent_ready: bool
    redis_enabled: bool

# ========== INITIALIZE APP ==========

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    docs_url="/docs"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== STARTUP/SHUTDOWN ==========

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Pathvancer Agentic Chatbot...")
    
    # Initialize embeddings
    if not settings.OPENROUTER_API_KEY:
        logger.error("❌ OPENROUTER_API_KEY not set")
        raise RuntimeError("OPENROUTER_API_KEY environment variable is required")
    
    init_embedding_service(settings.OPENROUTER_API_KEY)
    
    # Initialize agent
    init_agent()
    
    logger.info("✓ All services initialized successfully (using OpenRouter + Supabase)")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down...")
    session_manager.cleanup_old_sessions()

# ========== HEALTH CHECK ==========

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        embeddings_ready=get_embedding_service() is not None,
        agent_ready=get_agent() is not None,
        redis_enabled=session_manager.redis_client is not None
    )

# ========== CHAT ENDPOINT ==========

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    
    Process user message and return AI response
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        user_id = request.user_id or "anonymous"
        
        # Validate request
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get agent
        agent = get_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        # Process message
        response = agent.process_message(
            session_id=session_id,
            message=request.message,
            user_id=user_id
        )
        
        if response.get("route") == "error":
            raise HTTPException(status_code=500, detail=response["answer"])
        
        return ChatResponse(**response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========== SESSION ENDPOINTS ==========

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        if session_manager.redis_client:
            session_manager.redis_client.delete(f"session:{session_id}")
        else:
            if session_id in session_manager.in_memory_sessions:
                del session_manager.in_memory_sessions[session_id]
        
        return {"status": "deleted", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========== KNOWLEDGE BASE ENDPOINTS ==========

@app.get("/knowledge-base")
async def get_knowledge_base():
    """Get all knowledge base entries"""
    return {
        "total": len(knowledge_base.qa_pairs),
        "qa_pairs": knowledge_base.qa_pairs
    }

@app.post("/knowledge-base")
async def add_knowledge_base_entry(question: str, answer: str):
    """Add a new knowledge base entry"""
    try:
        knowledge_base.add_qa_pair(question, answer)
        return {
            "status": "added",
            "total": len(knowledge_base.qa_pairs)
        }
    except Exception as e:
        logger.error(f"Error adding KB entry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========== ROOT ==========

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
