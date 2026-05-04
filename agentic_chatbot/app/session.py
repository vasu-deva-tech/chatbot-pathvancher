import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

try:
    from supabase import create_client, Client
except ImportError:
    Client = None

from app.config import settings

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions with Supabase backend"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.in_memory_sessions: Dict[str, Dict] = {}
        
        # Try to initialize Supabase
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                # Test connection
                self.supabase.table(settings.SUPABASE_TABLE_SESSIONS).select("id").limit(1).execute()
                logger.info("✓ Supabase connected")
            except Exception as e:
                logger.warning(f"Supabase connection failed: {e}. Using in-memory storage.")
                self.supabase = None
        else:
            logger.warning("Supabase credentials not configured. Using in-memory storage.")
    
    def create_session(self, session_id: str, user_id: str = "anonymous") -> Dict:
        """Create a new user session"""
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "conversation_history": [],
            "context_data": {},
            "message_count": 0,
            "extracted_details": {}
        }
        
        self._save_session(session_id, session_data)
        return session_data
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session by ID"""
        try:
            if self.supabase:
                response = self.supabase.table(settings.SUPABASE_TABLE_SESSIONS).select("*").eq("session_id", session_id).execute()
                if response.data:
                    session_data = response.data[0]
                    # Parse JSON fields
                    if isinstance(session_data.get("conversation_history"), str):
                        session_data["conversation_history"] = json.loads(session_data["conversation_history"])
                    if isinstance(session_data.get("context_data"), str):
                        session_data["context_data"] = json.loads(session_data["context_data"])
                    if isinstance(session_data.get("extracted_details"), str):
                        session_data["extracted_details"] = json.loads(session_data["extracted_details"])
                    return session_data
            else:
                return self.in_memory_sessions.get(session_id)
        except Exception as e:
            logger.error(f"Error retrieving session: {e}")
        
        return None
    
    def _save_session(self, session_id: str, session_data: Dict):
        """Save session to Supabase or in-memory"""
        try:
            if self.supabase:
                # Prepare data for Supabase
                data_to_save = {
                    "session_id": session_id,
                    "user_id": session_data.get("user_id"),
                    "created_at": session_data.get("created_at"),
                    "last_activity": session_data.get("last_activity"),
                    "conversation_history": json.dumps(session_data.get("conversation_history", [])),
                    "context_data": json.dumps(session_data.get("context_data", {})),
                    "message_count": session_data.get("message_count", 0),
                    "extracted_details": json.dumps(session_data.get("extracted_details", {}))
                }
                
                # Upsert (insert or update)
                self.supabase.table(settings.SUPABASE_TABLE_SESSIONS).upsert(data_to_save).execute()
            else:
                self.in_memory_sessions[session_id] = session_data
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def update_session(self, session_id: str, updates: Dict) -> Dict:
        """Update an existing session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.update(updates)
        session["last_activity"] = datetime.utcnow().isoformat()
        self._save_session(session_id, session)
        return session
    
    def add_message_to_history(self, session_id: str, message: str, role: str = "user") -> Dict:
        """Add a message to conversation history"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        history_entry = {
            "role": role,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        session["conversation_history"].append(history_entry)
        session["message_count"] = session.get("message_count", 0) + 1
        
        # Keep only last N messages to save space
        if len(session["conversation_history"]) > settings.MAX_CONTEXT_HISTORY:
            session["conversation_history"] = session["conversation_history"][-settings.MAX_CONTEXT_HISTORY:]
        
        self._save_session(session_id, session)
        return session
    
    def get_conversation_context(self, session_id: str) -> str:
        """Get formatted conversation history as context"""
        session = self.get_session(session_id)
        if not session:
            return ""
        
        context_lines = []
        for entry in session.get("conversation_history", [])[-5:]:  # Last 5 messages
            role = entry.get("role", "user").upper()
            msg = entry.get("message", "")
            context_lines.append(f"{role}: {msg}")
        
        return "\n".join(context_lines)
    
    def update_extracted_details(self, session_id: str, details: Dict) -> Dict:
        """Update extracted customer details in session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session["extracted_details"].update(details)
        self._save_session(session_id, session)
        return session
    
    def cleanup_old_sessions(self):
        """Remove sessions older than timeout"""
        if self.supabase:
            try:
                # Calculate cutoff time
                cutoff_time = (datetime.utcnow() - timedelta(seconds=settings.SESSION_TIMEOUT)).isoformat()
                
                # Delete old sessions
                self.supabase.table(settings.SUPABASE_TABLE_SESSIONS).delete().lt("last_activity", cutoff_time).execute()
                logger.info("Cleaned up old sessions from Supabase")
            except Exception as e:
                logger.error(f"Error cleaning up sessions: {e}")
        else:
            # In-memory cleanup
            now = datetime.utcnow()
            expired = []
            for sid, data in self.in_memory_sessions.items():
                created = datetime.fromisoformat(data.get("created_at", ""))
                if now - created > timedelta(seconds=settings.SESSION_TIMEOUT):
                    expired.append(sid)
            
            for sid in expired:
                del self.in_memory_sessions[sid]
            
            if expired:
                logger.info(f"Cleaned up {len(expired)} expired sessions")

# Global session manager instance
session_manager = SessionManager()
