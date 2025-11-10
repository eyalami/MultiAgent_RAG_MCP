from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: Optional[str] = None  # User identifier for long-term persistence
    conversation_id: Optional[str] = None
    message: str = ""


class ChatResponse(BaseModel):
    conversation_id: Optional[str] = None
    message: List[str] = [""]