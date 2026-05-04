import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Config
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    API_TITLE: str = "PathVancer Agentic Chatbot"
    API_VERSION: str = "1.0.0"
    
    # OpenRouter Config (replaces OpenAI)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.io/api/v1"
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    
    # Supabase Config (replaces Redis)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_TABLE_SESSIONS: str = "sessions"
    SUPABASE_TABLE_MESSAGES: str = "messages"
    
    # Session Config
    SESSION_TIMEOUT: int = 3600  # 1 hour
    MAX_CONTEXT_HISTORY: int = 10
    
    # Knowledge Base
    KNOWLEDGE_BASE_FILE: str = os.getenv("KNOWLEDGE_BASE_FILE", "knowledge_base.json")
    
    # Thresholds
    SEMANTIC_THRESHOLD: float = 0.50
    INTENT_CONFIDENCE_THRESHOLD: float = 0.60
    
    # Features
    ENABLE_INTENT_DETECTION: bool = True
    ENABLE_SESSION_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
