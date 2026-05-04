# Frontend Integration Guide

This guide shows how to integrate the PathVancer Agentic Chatbot with your frontend application.

## Setup

### 1. Install Dependency

For React/Vue/Angular:
```bash
npm install axios
# or
npm install fetch # if using native fetch
```

### 2. Environment Configuration

```env
REACT_APP_CHATBOT_URL=http://localhost:8000
# or for production:
REACT_APP_CHATBOT_URL=https://your-deployed-chatbot.com
```

## React Example

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ChatbotWidget = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId] = useState(() => localStorage.getItem('chatbot_session_id') || generateSessionId());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    localStorage.setItem('chatbot_session_id', sessionId);
  }, [sessionId]);

  const generateSessionId = () => {
    return 'session_' + Math.random().toString(36).substr(2, 9);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', text: input }]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_CHATBOT_URL}/chat`,
        {
          message: input,
          session_id: sessionId,
          user_id: localStorage.getItem('user_email') || 'anonymous'
        },
        { timeout: 30000 }
      );

      // Add bot response to UI
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: response.data.answer,
        route: response.data.route,
        confidence: response.data.confidence
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: 'Sorry, I encountered an error. Please try again.',
        error: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot-widget">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.text}
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatbotWidget;
```

## Vue Example

```vue
<template>
  <div class="chatbot-widget">
    <div class="messages">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="`message ${msg.role}`"
      >
        {{ msg.text }}
      </div>
    </div>

    <form @submit.prevent="sendMessage">
      <input
        v-model="input"
        type="text"
        placeholder="Ask me anything..."
        :disabled="loading"
      />
      <button type="submit" :disabled="loading">Send</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ChatbotWidget',
  data() {
    return {
      messages: [],
      input: '',
      sessionId: this.getOrCreateSessionId(),
      loading: false,
      chatbotUrl: process.env.VUE_APP_CHATBOT_URL || 'http://localhost:8000'
    };
  },
  methods: {
    generateSessionId() {
      return 'session_' + Math.random().toString(36).substr(2, 9);
    },
    getOrCreateSessionId() {
      let sessionId = localStorage.getItem('chatbot_session_id');
      if (!sessionId) {
        sessionId = this.generateSessionId();
        localStorage.setItem('chatbot_session_id', sessionId);
      }
      return sessionId;
    },
    async sendMessage() {
      if (!this.input.trim()) return;

      this.messages.push({ role: 'user', text: this.input });
      const userMessage = this.input;
      this.input = '';
      this.loading = true;

      try {
        const response = await axios.post(
          `${this.chatbotUrl}/chat`,
          {
            message: userMessage,
            session_id: this.sessionId,
            user_id: localStorage.getItem('user_email') || 'anonymous'
          },
          { timeout: 30000 }
        );

        this.messages.push({
          role: 'assistant',
          text: response.data.answer,
          route: response.data.route
        });
      } catch (error) {
        this.messages.push({
          role: 'assistant',
          text: 'Sorry, I encountered an error. Please try again.',
          error: true
        });
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.chatbot-widget {
  max-width: 500px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.messages {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
  background: #f9f9f9;
}

.message {
  margin: 8px 0;
  padding: 8px 12px;
  border-radius: 4px;
}

.message.user {
  background: #007bff;
  color: white;
  text-align: right;
  margin-left: auto;
  max-width: 80%;
}

.message.assistant {
  background: #e9ecef;
  color: black;
  max-width: 80%;
}

form {
  display: flex;
  padding: 12px;
  border-top: 1px solid #ddd;
}

input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 8px;
}

button {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
```

## HTML/Vanilla JS

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    .chatbot-widget {
      max-width: 500px;
      border: 1px solid #ddd;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      font-family: Arial, sans-serif;
    }
    .messages {
      height: 400px;
      overflow-y: auto;
      padding: 16px;
      background: #f9f9f9;
    }
    .message {
      margin: 8px 0;
      padding: 8px 12px;
      border-radius: 4px;
      word-wrap: break-word;
    }
    .message.user {
      background: #007bff;
      color: white;
      text-align: right;
      margin-left: auto;
      max-width: 80%;
    }
    .message.assistant {
      background: #e9ecef;
      color: black;
      max-width: 80%;
    }
    .message.error {
      background: #f8d7da;
      color: #721c24;
    }
    form {
      display: flex;
      padding: 12px;
      border-top: 1px solid #ddd;
    }
    input {
      flex: 1;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
      margin-right: 8px;
    }
    button {
      padding: 8px 16px;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    button:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
  </style>
</head>
<body>
  <div class="chatbot-widget">
    <div id="messages" class="messages"></div>
    <form id="chatForm">
      <input id="input" type="text" placeholder="Ask me anything..." />
      <button type="submit">Send</button>
    </form>
  </div>

  <script>
    const CHATBOT_URL = 'http://localhost:8000';
    let sessionId = localStorage.getItem('chatbot_session_id') || generateSessionId();
    
    function generateSessionId() {
      const id = 'session_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('chatbot_session_id', id);
      return id;
    }

    document.getElementById('chatForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const input = document.getElementById('input');
      const message = input.value.trim();
      
      if (!message) return;

      // Add user message
      addMessage(message, 'user');
      input.value = '';
      input.disabled = true;

      try {
        const response = await fetch(`${CHATBOT_URL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: message,
            session_id: sessionId,
            user_id: localStorage.getItem('user_email') || 'anonymous'
          })
        });

        const data = await response.json();
        
        if (response.ok) {
          addMessage(data.answer, 'assistant');
        } else {
          addMessage('Error: ' + data.detail, 'assistant error');
        }
      } catch (error) {
        addMessage('Connection error. Please try again.', 'assistant error');
      } finally {
        input.disabled = false;
        input.focus();
      }
    });

    function addMessage(text, role) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `message ${role}`;
      msgDiv.textContent = text;
      document.getElementById('messages').appendChild(msgDiv);
      document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
    }
  </script>
</body>
</html>
```

## CORS Configuration

If your frontend is on a different domain, CORS is already enabled in the chatbot:

```python
# In app/main.py - CORS is configured for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Best Practices

1. **Session Management**
   - Store `session_id` in `localStorage` to maintain conversation history
   - Reset on logout

2. **Error Handling**
   - Always handle network errors
   - Show user-friendly error messages

3. **User Tracking**
   - Send `user_id` or email for tracking
   - Helps with analytics and support

4. **Performance**
   - Debounce rapid requests
   - Show loading indicator while waiting
   - Use reasonable timeouts (30s)

5. **Security**
   - Use HTTPS in production
   - Validate messages on frontend
   - Don't expose API keys in frontend code

## Testing

```bash
# Test local setup
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "session_id": "test-session",
    "user_id": "test@example.com"
  }'

# Expected response:
# {
#   "session_id": "test-session",
#   "user_id": "test@example.com",
#   "answer": "...",
#   "route": "kb|ai",
#   "confidence": "high|medium|low",
#   "is_new_session": true,
#   "message_count": 1,
#   "timestamp": "2024-..."
# }
```
