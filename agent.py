import os

from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)


set_tracing_disabled(True)

client = AsyncOpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url=os.environ["GEMINI_BASE_URL"],
)

model = OpenAIChatCompletionsModel(
    model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
    openai_client=client,
)


agent = Agent(
    name="General Task Agent",
    instructions="""
أنت وكيل ذكاء اصطناعي عام.

افهم مهمة المستخدم ونفذها بأفضل طريقة ممكنة.
كن واضحاً ومباشراً.
لا تدّعي تنفيذ شيء لم تنفذه فعلياً.

في هذه المرحلة أنت وكيل تجريبي، وسنضيف إليه أدوات حقيقية لاحقاً.
""",
    model=model,
)
