from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AiModel(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[float] = None

class GeminiChatMessage(BaseModel):
    role: str
    parts: List[str]

class OpenAIChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    type: str

class SessionInfo(BaseModel):
    session_id: str
    created_at: float
    message_count: int
    frustration_level: int


