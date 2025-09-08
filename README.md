# Chatbot Medical - Local (FastAPI + SQLite) - Arabic UI

## المتطلبات
- Python 3.10+ مثبت
- Visual Studio (أو Visual Studio Code). الإرشادات هنا تشتغل في بيئة Python داخل Visual Studio أيضاً.

## تشغيل محلي (خطوات)
1. افتح المشروع في Visual Studio.
2. افتح Terminal في المجلد الجذري (حيث requirements.txt).
3. أنشئ بيئة افتراضية:
   - Windows:
     python -m venv venv
     venv\Scripts\activate
4. ثبّت الحزم:
     pip install -r requirements.txt
5. (اختياري) ضع المفتاح الخاص بـ Gemini في متغير بيئة:
   - Windows (PowerShell):
     $env:GEMINI_API_KEY="PUT_YOUR_KEY"
   - لاحقاً ستغيّرون هذا لتخزين آمن أكثر.
   ملاحظة: إن لم تضعوا المفتاح، سيعمل النظام في وضع الـ mock تلقائيًا.
6. شغّل التطبيق:
     uvicorn app.main:app --reload
7. افتح المتصفح وادخل:
     http://127.0.0.1:8000/
8. اختبار:
   - جربوا سؤالاً طبيًا (مثال: "ما هي أعراض التهاب الرئة؟") وسيُرد برد تجريبي.
   - إن سألتم سؤالاً خارج الطب سيُرفض برفق: "أستطيع الإجابة فقط على الأسئلة الطبية..."

## ملاحظات مهمة
- الفلترة الطبية الآن تعتمد على قائمة كلمات (قابلة للتوسيع في app/utils.py).
- لتفعيل استدعاء حقيقي لـ Gemini: عدّلوا دالة call_gemini في app/utils.py واتّبعوا وثائق Google الرسمية لوضع الـ endpoint وطريقة الطلب.
- لا تضعوا مفتاح الـ API في الكلاينت أو في الكود؛ استعملوا متغيرات بيئة أو secret manager.

