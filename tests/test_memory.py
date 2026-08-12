from app.memory.short_term import InMemoryStore


def test_memory_is_bounded():
    store = InMemoryStore(max_messages=2)
    store.append("s1", "user", "one")
    store.append("s1", "assistant", "two")
    store.append("s1", "user", "three")

    assert [m["content"] for m in store.get("s1").messages] == ["two", "three"]
