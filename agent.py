import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# تحميل ملف .env لقراءة الـ API Key
load_dotenv()

# تهيئة العميل (سيقرأ المفتاح تلقائياً من بيئة النظام إذا كان اسمه GEMINI_API_KEY)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# قراءة اسم النموذج من ملف .env (أو استخدام قيمة افتراضية)
MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

def run_agent(message: str) -> str:
    try:
        # إرسال الطلب للنموذج
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=message,
            config=types.GenerateContentConfig(
                temperature=1.0,
                top_p=0.95,
                max_output_tokens=8192, # الحد الأقصى للمخرجات غالباً يكون 8192
            ),
        )
        # إرجاع النص
        return response.text
    
    except Exception as e:
        return f"حدث خطأ أثناء التواصل مع النموذج: {str(e)}"