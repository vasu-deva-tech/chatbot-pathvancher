"""
Example client for Pathvancer Agentic Chatbot

Shows how to integrate with the chatbot API
"""

import requests
import json
from typing import Dict, Optional
import uuid

class PathVancerChatbot:
    """Client for interacting with PathVancer Chatbot"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session_id = str(uuid.uuid4())
        self.user_id = "anonymous"
    
    def set_user(self, user_id: str):
        """Set user ID for tracking"""
        self.user_id = user_id
    
    def health_check(self) -> Dict:
        """Check if chatbot is healthy"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def send_message(self, message: str) -> Dict:
        """
        Send a message to the chatbot
        
        Args:
            message: User message
        
        Returns:
            Response dict with answer
        """
        payload = {
            "message": message,
            "session_id": self.session_id,
            "user_id": self.user_id
        }
        
        response = requests.post(
            f"{self.base_url}/chat",
            json=payload,
            timeout=30
        )
        
        return response.json()
    
    def get_session_history(self) -> Dict:
        """Get conversation history for current session"""
        response = requests.get(
            f"{self.base_url}/session/{self.session_id}"
        )
        return response.json()
    
    def get_knowledge_base(self) -> Dict:
        """Get all knowledge base entries"""
        response = requests.get(f"{self.base_url}/knowledge-base")
        return response.json()
    
    def add_knowledge(self, question: str, answer: str) -> Dict:
        """Add new Q&A to knowledge base"""
        response = requests.post(
            f"{self.base_url}/knowledge-base",
            params={"question": question, "answer": answer}
        )
        return response.json()


# ========== EXAMPLE USAGE ==========

if __name__ == "__main__":
    # Initialize client
    bot = PathVancerChatbot("http://localhost:8000")
    bot.set_user("john@example.com")
    
    # Check health
    print("🏥 Health Check:")
    health = bot.health_check()
    print(json.dumps(health, indent=2))
    
    # Send messages
    messages = [
        "Hello! What is Pathvancer?",
        "How can I get started?",
        "Tell me more about pricing"
    ]
    
    print("\n💬 Conversation:")
    for msg in messages:
        print(f"\nUser: {msg}")
        
        response = bot.send_message(msg)
        print(f"Bot: {response['answer']}")
        print(f"Route: {response['route']} | Confidence: {response['confidence']}")
    
    # Get session history
    print("\n📝 Session History:")
    history = bot.get_session_history()
    print(f"Messages: {history['message_count']}")
    
    # Get knowledge base
    print("\n📚 Knowledge Base:")
    kb = bot.get_knowledge_base()
    print(f"Total Q&A pairs: {kb['total']}")
