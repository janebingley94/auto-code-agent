from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.agent import router as agent_router

app = FastAPI(title="Auto Code Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "message": "Phase 1 core agent ready"}


app.include_router(agent_router)
