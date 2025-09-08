# # app/utils.py
# import os
# import google.generativeai as genai
# from datetime import datetime
#
# # ---------- إعدادات ----------
#API_KEY = "AIzaSyBboZ9q_BqfWB1yCGKSim9Fm9Au_NB6XKw"  # ← ضع مفتاحك هنا
#
# # --- system prompt بالعربي ---
# SYSTEM_PROMPT = """
# أنت مساعد تعليمي طبي مخصص لطلاب المادة. أجب فقط على الأسئلة المتعلقة بالطب...
# (نفس النص الطويل الذي وضعته سابقًا)
# شوف ركز على الاسئله الخاصه بكل جلسه بحيث اذا طلب منك لخص لي الاسئله السابقه اجب عليها او قيل لك ماهي الاسئ=له السابفه اجب عليها المهم خليك مركز
# """
#
# # ---------------------------
# # تخزين سجل المحادثة مؤقتًا لكل جلسة
# chat_history = []  # كل عنصر: {"question": "...", "answer": "...", "timestamp": ...}
#
# def call_gemini(user_message: str, system_prompt: str = SYSTEM_PROMPT, history=None) -> str:
#     """
#     استدعاء Gemini للرد على رسالة المستخدم مع أخذ المحادثات السابقة بالحسبان.
#     """
#     api_key = API_KEY
#     if not api_key:
#         return "[خطأ: لم يتم ضبط المفتاح داخل utils.py]"
#
#     try:
#
#         client = genai.Client(api_key=api_key)
#
#         # بناء prompt مع إضافة سجل المحادثة السابقة
#         prompt = system_prompt + "\n\n"
#         if history:
#             for entry in history:
#                 sender = entry.get("sender", "user")
#                 content = entry.get("content", "")
#                 if not content:
#                     continue
#                 if sender in ("bot", "assistant", "model"):
#                     prompt += f"Bot: {content}\n"
#                 else:
#                     prompt += f"User: {content}\n"
#         else:
#             for entry in chat_history:
#                 prompt += f"User: {entry['question']}\nBot: {entry['answer']}\n"
#
#         prompt += f"User: {user_message}"
#
#         # استدعاء النموذج
#         model_name = "gemini-2.5-flash"
#         response = client.models.generate_content(
#             model=model_name,
#             contents=prompt
#         )
#
#         # استخراج النص من الاستجابة
#         if hasattr(response, "text") and response.text:
#             answer = response.text.strip()
#         elif hasattr(response, "candidates") and response.candidates:
#             parts = []
#             for cand in response.candidates:
#                 if hasattr(cand, "content"):
#                     parts.append(str(cand.content))
#             answer = "\n".join(parts).strip()
#         else:
#             answer = str(response)
#
#         # تحديث سجل المحادثة
#         chat_history.append({
#             "question": user_message,
#             "answer": answer,
#             "timestamp": datetime.utcnow()
#         })
#
#         return answer
#
#     except Exception as e:
#         return f"خطاء في اتصالك بالأنترنت تأكد انك متصل ثم اعد المحاولة: {str(e)}"
# ------------------------------------
#----------------------------
# app/utils.py
import os
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


# ---------- إعدادات ----------


# --- system prompt ---
SYSTEM_PROMPT = """
أنت مساعد تعليمي طبي مخصص لطلاب المادة. أجب فقط على الأسئلة المتعلقة بالطب (تشريح، فسيولوجي، أمراض، علاج أساسي، تشخيص سريري تعليمي).
إذا السؤال خارج نطاق الطب، أجب: "أستطيع الإجابة فقط على الأسئلة الطبية المتعلقة بالمقرر؛ ."
لا تعط وصفات صريحة أو نصائح طبية طارئة. إذا يبدو أنه حالة طارئة، قل: "هذه تبدو حالة طارئة؛ يرجى الاتصال بخدمات الطوارئ".
اذا تم سؤالك من انت او من برمجك او من طورك اجب تم تصميمي بواسطه المهندسان  هيثم عمران و احمد الغيلي 
واذا قيل لك السلام عليكم اجيب عليه بتحية الاسلام كاملة و اضف انك شات بوت متخصص في مجال الطب وتم تطويرك من قبل هيثم عمران واحمد الغيلي
كن مهذبًا، ودودًا، ومختصرًا. استخدم لغة بسيطة ومباشرة.
استخدم أمثلة عملية عند الشرح. لا تستخدم المصطلحات التقنية المعقدة بدون شرح.
إذا لم تعرف الإجابة، قل ببساطة: "لا أعرف".
لا تدع المستخدم يمل منك وكن لطيفًا في ردودك. و تكلم معه بكلام انك تقدر تساعده في الطب
اهم شيء المهندس لا تنساه في اغلب كلامك تقديرا وشكرا له
عند ذكرك للمهندس اضف له مدح من عندك يليق بهم
و اذا طلب منك المستخدم ان تذكر من طورك او من برمجك اذكر المهندسان هيثم عمران و احمدالغيلي  
ودلع المستخدم ايضا بالكلام مثلا اهلا وسهلا بك عزيزي في الشات الطبي تفضل كيف يمكنني مساعدتك اليوم  
-المهندسين ليس في الاجابت العلميه يذكروا غالبا بل بالقليل ولكن ما دون السؤال العلمي مثلا ترحيب 
-رتب كلامك و اجعل اجابتك مرتبه و منظمة
-ولا تجعلها فوق بعض اعطي كل كلام حقه من التصميم و التنسيق
تنسيق اجابتك يكون سطور مرتبه ونقاط وغيرها
-اذا تم سؤالك في مجال الطب رد بادب واحترام نوع اجابتك تعاريف نقاط ومصطلحات طبيه 
كذلك اذا اراد المستخدم تزوده بمراجع علميه او مواقع بحوثات زوده 
اذا اراد ان تشرح له عن ماده في مجال الطب اشرح له حتى لم لم يكن محدد المهم الماده في مجال الطب
استقبله بكل معاني الترحيب والاحترام اجعله يشعر بانه في المكان الصح وانه لا يمل من الكلام معك 
قل له انك استمتعت بالحديث معه وانه اذا كان هنالك اي سؤال لا يتردد في ارساله 
كذلك استخدم الايموجي ليشعر المستخدم بانك تحترمه ومستمتع في الشرح كثيرا 
رتب له الاجابات بشكل حلو   
في حال اراد الخروج او شكرك قل له العفو كل الشكر لمن قاما بتطويري
بامكانك الرد عليه اذا كان الكلام انجليزي باي لغه كانت وترجم له مايريد المهم الموضوع لا يخرج عن مجال الطب
اذا تم سؤالك باللغه الانجليزيه رد بالانجليزيه واذا اراد الرد يكون عربي والسؤال انجليزي لا مانع 
الأسلوب والشخصية**:
   - كن مهذبًا، ودودًا، ولطيفًا مع المستخدم.  
   - استخدم لغة بسيطة وواضحة، مع أمثلة عملية عند الحاجة.  
   - نظم الإجابات على شكل نقاط أو فقرات مفصّلة.  
   - أضف إيموجي للمحادثه حسنها 🙂.  
   - استقبل المستخدم بالترحيب الكامل: "أهلاً وسهلاً بك عزيزي في الشات الطبي! تفضل كيف يمكنني مساعدتك اليوم؟"  
   - دلّع المستخدم بأدب وود في جميع الردود. 
   - لا تستقبل المستخدم بالترحب بالسلام في كل اجابه فقط عند الرسالة الاولى رحب به  
   - من الافضل ان تجعل الرد حقك منظم وتخليه متباعد وتستخدم تعدد النقاط 
   -الاختصار في الكلام لو كان الرد كبير  

**التنسيق الإضافي**:
   - اجعل كل إجابة تحتوي على عناوين فرعية واضحة.  
   - في بداية العناوين استخدم إيموجي مناسب مثل: 📌 ✨ 💊 🧠 🧾 … حسب الموضوع.  
   - استخدم الترقيم (1، 2، 3) عند عرض القوائم.  
   - ضع مسافات كافية بين الفقرات لسهولة القراءة.  
   - إذا كان المحتوى طويلًا، قدم ملخصًا قصيرًا في النهاية.  

**اللغة**:
   - إذا كان السؤال بالعربية، أجب بالعربية.  
   - إذا كان السؤال بالإنجليزية، أجب بالإنجليزية.  
"""



# ---------------------------
chat_history = []  # كل عنصر: {"question": "...", "answer": "...", "timestamp": ...}

def call_gemini(user_message: str, system_prompt: str = SYSTEM_PROMPT, history=None) -> str:
    """
    استدعاء Gemini للرد على رسالة المستخدم مع أخذ المحادثات السابقة بالحسبان.
    """
    if not API_KEY:
        raise ValueError("API_KEY not found in environment variables.")

    try:
        # تهيئة المكتبة بالمفتاح
        genai.configure(api_key=API_KEY)

        # بناء prompt مع سجل المحادثة
        prompt = system_prompt + "\n\n"
        if history:
            for entry in history:
                sender = entry.get("sender", "user")
                content = entry.get("content", "")
                if not content:
                    continue
                if sender in ("bot", "assistant", "model"):
                    prompt += f"Bot: {content}\n"
                else:
                    prompt += f"User: {content}\n"
        else:
            for entry in chat_history:
                prompt += f"User: {entry['question']}\nBot: {entry['answer']}\n"

        prompt += f"User: {user_message}"

        # استدعاء النموذج
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # استخراج النص من الاستجابة
        answer = response.text.strip() if hasattr(response, "text") else str(response)

        # تحديث السجل
        chat_history.append({
            "question": user_message,
            "answer": answer,
            "timestamp": datetime.utcnow()
        })

        return answer

    except Exception as e:
        return f"خطاء في اتصالك بالأنترنت تأكد انك متصل ثم اعد المحاولة: {str(e)}"

