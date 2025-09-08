# #-----------------------------------------------------------
# #-----------------------------------------------------------
# #-----------------------------------------------------------
# #-----------------------------------------------------------
# #-----------------------------------------------------------
# نماذج قاعدة البيانات (ChatSession، Message، Feedback)
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class ChatSession(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="جلسة طالب")
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    sender = Column(String(20))  # "user" أو "bot"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("ChatSession", back_populates="messages")

# class Feedback(Base):
#     __tablename__ = "feedbacks"
#     id = Column(Integer, primary_key=True, index=True)
#     message_id = Column(Integer)  # يمكن ربطه إلى messages.id إن رغبت
#     rating = Column(Integer)      # 1..5
#     comment = Column(Text, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
