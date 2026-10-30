from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Notion AI Agent",
    description="AI agent for managing a Notion workspace",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(
    router
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "application": "Notion AI Agent"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }