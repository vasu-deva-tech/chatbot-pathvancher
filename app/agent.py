from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, List, Optional, Tuple
import logging

from app.config import settings
from app.session import session_manager
from app.knowledge_base import knowledge_base
from app.embeddings import get_embedding_service
from app.tools.core_tools import CHATBOT_TOOLS

logger = logging.getLogger(__name__)

class ChatbotAgent:
    """Main agent for chatbot conversation"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Pathvancer's AI support assistant. 
            
Your responsibilities:
1. Help customers with questions about our services
2. Extract and remember company details
3. Detect buying intent
4. Provide helpful, concise responses (2-4 sentences)
5. Use session context for personalized responses
6. Always be professional and helpful

Use the available tools to:
- Detect buying intent
- Extract company details
- Validate session data
- Build appropriate responses

If you don't have information, direct them to: info@pathvancer.com"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.agent = create_tool_calling_agent(
            self.llm,
            CHATBOT_TOOLS,
            self.prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=CHATBOT_TOOLS,
            verbose=False,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def process_message(self, session_id: str, message: str, user_id: str = "anonymous") -> Dict:
        """
        Process user message and generate response
        
        Args:
            session_id: Unique session identifier
            message: User message
            user_id: User identifier
        
        Returns:
            Response dict with answer and metadata
        """
        try:
            # Get or create session
            session = session_manager.get_session(session_id)
            if not session:
                session = session_manager.create_session(session_id, user_id)
                is_new_session = True
            else:
                is_new_session = False
            
            # Add user message to history
            session_manager.add_message_to_history(session_id, message, "user")
            
            # Get embedding service
            embedding_svc = get_embedding_service()
            if not embedding_svc:
                return self._error_response(session_id, "Embedding service not available")
            
            # Get message embedding for semantic search
            query_embedding = embedding_svc.get_embedding(message)
            
            # Search knowledge base
            kb_results = knowledge_base.search(
                message,
                embedding_svc.get_embedding,
                top_k=3
            )
            
            # Prepare context
            chat_history = self._build_chat_history(session)
            context_str = session_manager.get_conversation_context(session_id)
            
            # Build input for agent
            kb_context = ""
            if kb_results and kb_results[0]["similarity"] > settings.SEMANTIC_THRESHOLD:
                best_match = kb_results[0]
                kb_context = f"\n\nKnowledge Base Match (confidence: {best_match['similarity']:.2%}):\nQ: {best_match['question']}\nA: {best_match['answer']}"
                route = "kb"
                answer = best_match["answer"]
            else:
                kb_context = "\n\nNo high-confidence matches in knowledge base. Generate helpful response."
                route = "ai"
                answer = None
            
            # Run agent
            agent_input = f"""Process this customer message:
            
Message: {message}

{kb_context}

Previous context: {context_str if context_str else 'New session'}

Please:
1. Detect any buying intent
2. Extract company details if available
3. Provide a helpful response"""
            
            result = self.executor.invoke({
                "input": agent_input,
                "chat_history": chat_history,
                "agent_scratchpad": ""
            })
            
            # Extract response from agent output
            agent_output = result.get("output", "")
            
            # If we have KB match, use it; otherwise use agent output
            if route == "kb":
                final_answer = answer
            else:
                final_answer = agent_output
            
            # Add bot response to history
            session_manager.add_message_to_history(session_id, final_answer, "assistant")
            
            # Prepare response
            response = {
                "session_id": session_id,
                "user_id": user_id,
                "answer": final_answer,
                "route": route,
                "is_new_session": is_new_session,
                "message_count": session.get("message_count", 0),
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "confidence": "high" if route == "kb" and kb_results[0]["similarity"] > 0.75 else "medium"
            }
            
            logger.info(f"✓ Session {session_id}: {route.upper()} route, message #{session.get('message_count')}")
            
            return response
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._error_response(session_id, str(e))
    
    def _build_chat_history(self, session: Dict) -> List:
        """Build chat history for context"""
        messages = []
        for entry in session.get("conversation_history", [])[-5:]:  # Last 5 messages
            role = entry.get("role", "user")
            msg = entry.get("message", "")
            
            if role == "user":
                messages.append(HumanMessage(content=msg))
            elif role == "assistant":
                messages.append(AIMessage(content=msg))
        
        return messages
    
    def _error_response(self, session_id: str, error: str) -> Dict:
        """Create error response"""
        return {
            "session_id": session_id,
            "answer": f"I encountered an error: {error}. Please try again.",
            "route": "error",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
            "confidence": "low"
        }

# Global agent instance
chatbot_agent: Optional[ChatbotAgent] = None

def init_agent():
    """Initialize the chatbot agent"""
    global chatbot_agent
    chatbot_agent = ChatbotAgent()
    logger.info("✓ Chatbot agent initialized")

def get_agent() -> Optional[ChatbotAgent]:
    """Get the chatbot agent instance"""
    return chatbot_agent
