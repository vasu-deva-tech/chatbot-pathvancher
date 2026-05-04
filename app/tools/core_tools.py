import re
import json
from typing import Dict, List, Optional, Tuple
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

# ========== INTENT DETECTION TOOLS ==========

@tool
def detect_buying_intent(message: str) -> Dict:
    """
    Detect if user has buying intent
    
    Args:
        message: User message
    
    Returns:
        Dict with intent level (high/medium/low) and matching keywords
    """
    text = message.lower()
    
    high_intent_words = [
        'buy', 'purchase', 'order', 'how much', 'price', 'cost',
        'checkout', 'payment', 'urgent', 'asap', 'need now',
        'kitne ka', 'lena hai', 'buy now', 'place order'
    ]
    
    medium_intent_words = [
        'interested', 'available', 'stock', 'dm me',
        'link', 'website', 'delivery', 'shipping', 'webinar', 'join', 'fees'
    ]
    
    high_matches = [w for w in high_intent_words if w in text]
    medium_matches = [w for w in medium_intent_words if w in text]
    
    if high_matches:
        intent_level = "high"
    elif medium_matches:
        intent_level = "medium"
    else:
        intent_level = "low"
    
    return {
        "intent_level": intent_level,
        "has_buying_intent": intent_level in ["high", "medium"],
        "high_matches": high_matches,
        "medium_matches": medium_matches
    }

# ========== COMPANY DETAIL EXTRACTION TOOLS ==========

@tool
def extract_company_details(message: str) -> Dict:
    """
    Extract company details (website, email, phone) from user message
    
    Args:
        message: User message
    
    Returns:
        Dict with extracted company details
    """
    # Website pattern
    website_pattern = r'(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})(?:\/[^\s]*)?'
    websites = re.findall(website_pattern, message)
    
    # Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, message)
    
    # Phone pattern
    phone_pattern = r'(?:\+?[0-9]{1,3}[-.\\s]?)?(?:\(?[0-9]{1,4}\)?[-.\\s]?)?[0-9]{1,4}[-.\\s]?[0-9]{1,4}[-.\\s]?[0-9]{1,9}'
    phones = re.findall(phone_pattern, message)
    
    # Extract name from first line if possible
    lines = message.split('\n')
    company_name = ""
    for line in lines:
        if any(keyword in line.lower() for keyword in ['company', 'business', 'organization']):
            company_name = line.replace('company:', '').replace('business:', '').replace('organization:', '').strip()
            break
    
    if not company_name and lines:
        company_name = lines[0][:100]
    
    return {
        "company_name": company_name,
        "website": websites[0] if websites else "",
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "all_websites": websites,
        "all_emails": emails,
        "all_phones": phones,
        "has_company_details": bool(websites or emails or phones)
    }

# ========== RESPONSE FORMATTING TOOLS ==========

@tool
def format_response(content: str, session_id: str, route: str = "kb") -> Dict:
    """
    Format response for the API
    
    Args:
        content: Response content
        session_id: User session ID
        route: Route taken (kb=knowledge base, ai=ai generated, unknown=not found)
    
    Returns:
        Formatted response dict
    """
    return {
        "session_id": session_id,
        "answer": content,
        "route": route,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }

# ========== CONTEXT BUILDING TOOLS ==========

@tool
def build_system_prompt(session_context: str, company_details: Dict) -> str:
    """
    Build system prompt for AI agent
    
    Args:
        session_context: Previous conversation context
        company_details: Extracted company details
    
    Returns:
        System prompt string
    """
    prompt = """You are Pathvancer's AI support assistant with session memory.

Your role:
- Provide helpful, clear responses in 2-4 sentences
- Use conversation history for context-aware answers
- Reference previous questions if relevant
- Always end with: "Would you like more details?"
- If unknown, respond: "I don't have that information. Contact: info@pathvancer.com"

"""
    
    if session_context:
        prompt += f"\nRecent Conversation:\n{session_context}\n"
    
    if company_details and company_details.get("has_company_details"):
        details_str = []
        if company_details.get("company_name"):
            details_str.append(f"Company: {company_details['company_name']}")
        if company_details.get("email"):
            details_str.append(f"Email: {company_details['email']}")
        if company_details.get("website"):
            details_str.append(f"Website: {company_details['website']}")
        
        if details_str:
            prompt += f"\nCustomer Details:\n" + "\n".join(details_str) + "\n"
    
    return prompt

# ========== VALIDATION TOOLS ==========

@tool
def validate_session_data(session_data: Dict) -> Tuple[bool, str]:
    """
    Validate session data
    
    Args:
        session_data: Session data to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["session_id", "user_id", "message"]
    
    for field in required_fields:
        if field not in session_data or not session_data[field]:
            return False, f"Missing required field: {field}"
    
    if not isinstance(session_data["session_id"], str):
        return False, "session_id must be a string"
    
    return True, ""

# ========== CONVERSATION MANAGEMENT TOOLS ==========

@tool
def extract_question_metadata(message: str) -> Dict:
    """
    Extract metadata about the question
    
    Args:
        message: User message
    
    Returns:
        Dict with question metadata
    """
    words = message.split()
    
    return {
        "word_count": len(words),
        "is_question": "?" in message or any(q in message.lower() for q in ['what', 'when', 'where', 'who', 'why', 'how', 'can', 'could']),
        "is_followup": any(f in message.lower() for f in ['more', 'also', 'what about', 'tell me', 'continue', 'explain']),
        "length": "short" if len(words) <= 4 else "medium" if len(words) <= 12 else "long"
    }

# Collect all tools
CHATBOT_TOOLS = [
    detect_buying_intent,
    extract_company_details,
    format_response,
    build_system_prompt,
    validate_session_data,
    extract_question_metadata
]
