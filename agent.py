import os
from google import genai
from dotenv import load_dotenv

# تحميل المتغيرات
load_dotenv()

# تهيئة العميل
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# سنقرأ اسم النموذج من Railway، وإذا لم يكن موجوداً سنستخدم النموذج الجديد
MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-3.1-pro-preview")

def run_agent(message: str) -> str:
    try:
        # استخدام Interactions API كما طلبت رسالة الخطأ (وكما كان كودك الأصلي)
        interaction = client.interactions.create(
            model=MODEL_ID,
            input=message,
            generation_config={
                "thinking_level": "high",
                "temperature": 1.0,
                "max_output_tokens": 65536,
                "top_p": 0.95,
            },
        )

        return interaction.output_text
    
    except Exception as e:
        return f"حدث خطأ أثناء التواصل مع نموذج جوجل: {str(e)}"