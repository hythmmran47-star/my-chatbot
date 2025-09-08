# app/schemas.py
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_id: Optional[str] = None     # اختياري (الواجهة قد ترسله)
    session_id: Optional[int] = None  # id الجلسة من DB (اختياري لإنشاء جلسة جديدة)
    message: str

class ChatResponse(BaseModel):
    reply: str
    message_id: Optional[int] = None
    session_id: Optional[int] = None

# class FeedbackRequest(BaseModel):
#     message_id: int
#     rating: int
#     comment: Optional[str] = None
