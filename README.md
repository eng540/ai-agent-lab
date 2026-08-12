# AI Agent Lab

Experimental Agent Runtime built around a replaceable model provider.

## V2

V2 introduces:

- FastAPI API layer
- provider abstraction for Gemini
- session IDs and run IDs
- bounded short-term conversation memory
- structured agent responses
- clear separation between API, runtime, memory, and model provider

## Run

Set `GEMINI_API_KEY` and optionally `GEMINI_MODEL`, then run:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Health:

`GET /`

Ask:

`POST /ask`

```json
{
  "message": "Hello",
  "session_id": "optional-session-id"
}
```

## Architecture

```text
FastAPI
  -> API Router
      -> Agent Runtime
          -> Session Memory
          -> Model Provider (Gemini)
```

The runtime is intentionally small. Tools, persistent memory, planning, execution loops, and observability are planned as subsequent layers rather than hidden inside the model provider.
