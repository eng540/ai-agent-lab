"""Deterministic verification layer.

Verification must not consume another LLM request. The executor already returns
explicit tool results; this module evaluates those results conservatively.
"""


def verify_task(goal: str, results: list[dict]) -> dict:
    if not results:
        return {
            "status": "failed",
            "reason": "لم يتم تنفيذ أي خطوة.",
            "next_action": "إعادة تشغيل المهمة بعد التأكد من توفر النموذج والحصة.",
        }

    failed = [r for r in results if r.get("status") == "failed"]
    if failed:
        return {
            "status": "failed" if len(failed) == len(results) else "partial",
            "reason": f"فشلت {len(failed)} من {len(results)} خطوة/خطوات.",
            "next_action": "مراجعة نتيجة الخطوة الفاشلة وإعادة تنفيذها.",
        }

    return {
        "status": "passed",
        "reason": f"تم تنفيذ {len(results)} خطوة دون أخطاء مُبلّغ عنها.",
        "next_action": "لا يوجد إجراء مطلوب.",
    }
