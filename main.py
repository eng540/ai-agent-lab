from fastapi import FastAPI

from app.api import router

app = FastAPI(
    title="AI Agent Lab",
    version="2.0.0",
    description="Experimental Agent Runtime with provider abstraction and session memory.",
)

app.include_router(router)
