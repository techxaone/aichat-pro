"""
AIChat Pro — Core Chatbot Engine (Groq Version — FREE)
Handles: Chat, Memory, Streaming, System Prompts
"""

from groq import Groq
from config import config
from typing import List, Dict, Generator


class Chatbot:
    def __init__(self, system_prompt: str = None):
        if not config.GROQ_API_KEY:
            raise ValueError(
                "❌ GROQ_API_KEY not found. Please add it to .env file."
            )
        
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL
        self.history: List[Dict] = []
        
        self.system_prompt = system_prompt or (
            "You are AIChat Pro, a helpful, friendly, and intelligent AI assistant. "
            "You provide clear, accurate, and detailed responses. "
            "When explaining technical concepts, use examples. "
            "Be concise but thorough."
        )
    
    def _build_messages(self, user_message: str) -> List[Dict]:
        """Build message list for API call"""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history[-config.MAX_HISTORY:])
        messages.append({"role": "user", "content": user_message})
        return messages
    
    def chat(self, user_message: str) -> str:
        """Non-streaming chat"""
        messages = self._build_messages(user_message)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )
        
        assistant_message = response.choices[0].message.content
        
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def stream_chat(self, user_message: str) -> Generator[str, None, None]:
        """Streaming chat — yields chunks"""
        messages = self._build_messages(user_message)
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            stream=True,
        )
        
        full_response = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
        
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": full_response})
    
    def clear_history(self):
        """Clear chat history"""
        self.history = []
    
    def get_history(self) -> List[Dict]:
        """Return history"""
        return self.history
    
    def set_system_prompt(self, prompt: str):
        """Update system prompt"""
        self.system_prompt = prompt
    
    def export_chat(self) -> str:
        """Export chat as markdown"""
        lines = ["# AIChat Pro — Conversation\n"]
        for msg in self.history:
            role = "👤 You" if msg["role"] == "user" else "🤖 Assistant"
            lines.append(f"### {role}\n\n{msg['content']}\n\n---\n")
        return "\n".join(lines)