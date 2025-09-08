# create_tables.py
from app.db import Base, engine
# from app.models import ChatSession, Message, Feedback

# هذا السطر ينشئ الجداول في قاعدة بيانات MySQL
Base.metadata.create_all(bind=engine)

print("تم إنشاء الجداول بنجاح!")
