from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.db.database import engine, Base
from app.api import authorize, events, policies, sessions

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (if they don't exist yet)
    Base.metadata.create_all(bind=engine)
    print(f"[startup] {settings.app_name} v{settings.app_version} ready")
    yield
    print("[shutdown] Policy engine shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Zero Trust IAM Policy Engine — verifies every access request",
    lifespan=lifespan,
)

# Allow dashboard to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────
app.include_router(authorize.router, prefix="/api",      tags=["Authorization"])
app.include_router(events.router,    prefix="/api",      tags=["Events"])
app.include_router(policies.router,  prefix="/api",      tags=["Policies"])
app.include_router(sessions.router,  prefix="/api",      tags=["Sessions"])


# ── Health check ──────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Zero Trust Policy Engine", "docs": "/docs"}
