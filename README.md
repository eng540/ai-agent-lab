# AI Agent Lab

Experimental Agent Runtime built around a replaceable model provider.

## Current architecture

```text
FastAPI
  -> API Router
      -> Agent Runtime
          -> Session Memory
          -> Model Provider (Gemini)
          -> Tool Registry
              -> Tool Executor
                  -> Registered Tools
```

## V2 — Runtime foundation

- provider abstraction for Gemini
- session IDs and run IDs
- bounded short-term conversation memory
- structured request/response schemas
- separation between API, runtime, memory, and provider

## V3 — Tool system foundation

- typed tool abstraction
- central tool registry
- isolated tool executor
- explicit confirmation gate for protected tools
- safe built-in `echo` tool for runtime tests
- `GET /tools` for tool metadata

The runtime deliberately does not execute arbitrary shell commands, code, network requests, or repository writes. Those capabilities should be added as explicitly scoped tools with their own permission model and tests.

## Run

Set `GEMINI_API_KEY` and optionally `GEMINI_MODEL`, then run:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Health:

`GET /`

Tool metadata:

`GET /tools`

Ask:

`POST /ask`

```json
{
  "message": "Hello",
  "session_id": "optional-session-id"
}
```

## Roadmap

1. V4 agent loop: plan → execute → observe → reflect.
2. Persistent project memory and run/event records.
3. GitHub, filesystem, web, and HTTP tools with explicit permissions.
4. Observability: structured logs, traces, latency, token/tool metrics.
5. Evaluation suite and CI gates.
6. Multi-agent orchestration only after the single-agent runtime is stable.
