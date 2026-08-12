"""Deterministic, quota-free verification layer."""


def verify_task(goal: str, results: list[dict]) -> dict:
    if not results:
        return {"status": "failed", "reason": "لم يتم تنفيذ أي خطوة.", "next_action": "إعادة تشغيل المهمة."}

    failed = [r for r in results if r.get("status") == "failed"]
    if failed:
        status = "failed" if len(failed) == len(results) else "partial"
        return {
            "status": status,
            "reason": f"فشلت {len(failed)} من {len(results)} خطوة/خطوات.",
            "next_action": "مراجعة الخطوة الفاشلة ثم إعادة تنفيذها.",
        }

    return {
        "status": "passed",
        "reason": f"تم تنفيذ {len(results)} خطوة دون أخطاء مُبلّغ عنها.",
        "next_action": "لا يوجد إجراء مطلوب.",
    }
