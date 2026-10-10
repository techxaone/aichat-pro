"""
AIChat Pro — Configuration (Groq Version — FREE)
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Groq API (FREE — https://console.groq.com/keys)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Groq Model (all FREE)
    # - llama-3.3-70b-versatile (best quality)
    # - llama-3.1-8b-instant (fastest)
    # - mixtral-8x7b-32768 (long context)
    # - gemma2-9b-it (small & fast)
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # App
    APP_NAME = "AIChat Pro"
    APP_VERSION = "1.0.0"
    MAX_HISTORY = 20
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    
    # Documents
    DOCS_DIR = "data/documents"
    VECTORSTORE_DIR = "data/vectorstore"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Validation
    @classmethod
    def is_valid(cls):
        return bool(cls.GROQ_API_KEY and cls.GROQ_API_KEY.startswith("gsk_"))


config = Config()