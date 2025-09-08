# app/main.py
# نقطة البداية: FastAPI app تستضيف الواجهة static وتوفّر نقاط النهاية المطلوبة
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

# استيراد إعدادات DB والنماذج
from .db import SessionLocal, engine, Base
from . import models, schemas, utils

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chatbot Medical - Arabic")

# استضافة مجلد static (index.html, app.js, style.css)
app.mount("/static", StaticFiles(directory="static"), name="static")


# دالة مساعدة للحصول على Session من SQLAlchemy
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------
# نقطة النهاية: صفحة الواجهة (تعيد index.html)
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


# -------------------------------------------
# API: استقبال رسالة دردشة
@app.post("/api/chat", response_model=schemas.ChatResponse)
async def chat_endpoint(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    # 2)تحميل أو إنشاء جلسة
    session = None
    if req.session_id:
        session = db.query(models.ChatSession).filter(models.ChatSession.id == req.session_id).first()
    if not session:
        session = models.ChatSession(name="جلسة طالب")
        db.add(session)
        db.commit()
        db.refresh(session)

    # 3)  حفظ رسالة المستخدم في DB
    msg = models.Message(session_id=session.id, sender="user", content=req.message)
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # 4) تجهيز تاريخ المحادثة وتمريره للنموذج (استذكار نفس الجلسة)
    msgs_hist = db.query(models.Message).filter(models.Message.session_id == session.id).order_by(
        models.Message.created_at).all()
    # استبعد آخر رسالة (هي رسالة المستخدم الحالية) لتفادي تكرارها، واحتفظ فقط بآخر 20 رسالة قبلها
    prev_msgs = msgs_hist[:-1] if len(msgs_hist) > 0 else []
    history = [{"sender": m.sender, "content": m.content} for m in prev_msgs][-20:]

    reply_text = utils.call_gemini(req.message, history=history)

    # 5)  حفظ رد البوت في DB
    bot_msg = models.Message(session_id=session.id, sender="bot", content=reply_text)
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    # 6)إعادة الرد
    return {"reply": reply_text, "message_id": bot_msg.id, "session_id": session.id}


# -------------------------------------------
# API: استرجاع التاريخ الخاص بجلسة
@app.get("/api/history")
async def get_history(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="جلسة غير موجودة")
    # بناء قائمة الرسائل مرتبة زمنياً
    msgs = db.query(models.Message).filter(models.Message.session_id == session_id).order_by(
        models.Message.created_at).all()
    out = [{"id": m.id, "sender": m.sender, "content": m.content, "created_at": m.created_at.isoformat()} for m in msgs]
    return {"session": {"id": session.id, "name": session.name, "created_at": session.created_at}, "messages": out}

# # -------------------------------------------
# # API: استقبال تقييم / ملاحظات
# @app.post("/api/feedback")
# async def feedback_endpoint(fb: schemas.FeedbackRequest, db: Session = Depends(get_db)):
#     # تأكد من أن التقييم داخل 1-5
#     if fb.rating < 1 or fb.rating > 5:
#         raise HTTPException(status_code=400, detail="التقييم يجب أن يكون بين 1 و 5")
#     entry = models.Feedback(message_id=fb.message_id, rating=fb.rating, comment=fb.comment)
#     db.add(entry)
#     db.commit()
#     db.refresh(entry)
#     return {"status": "ok", "id": entry.id}

# -------------------------------------------
# # API: endpoint بسيط لترخيص الادمن لمسح الجلسات (غير مؤمن هنا، للتجربة فقط)
# @app.post("/api/admin/flush")
# async def admin_flush(password: str):
#     # ملاحظة: في بيئة حقيقية استخدموا Authentication قوية!
#     if password != os.getenv("ADMIN_PASSWORD", "admin123"):
#         raise HTTPException(status_code=403, detail="غير مخوّل")
#     # نحذف ملف DB (بسيط للتطوير). في الإنتاج يجب تنظيف الجداول بشكل منضبط.
#     try:
#         os.remove("chatbot.db")
#         # ثم نعيد إنشاء الجداول
#         Base.metadata.create_all(bind=engine)
#     except Exception:
#         pass
#     return {"status": "db flushed"}

