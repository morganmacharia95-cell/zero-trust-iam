from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.scorer import calculate_risk

app = FastAPI(
    title="Zero Trust Risk Engine",
    version="0.1.0",
    description="Evaluates contextual risk signals for every access request",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScoreRequest(BaseModel):
    user_id:    str
    username:   str = ""
    ip_address: str = "127.0.0.1"
    user_agent: str = ""


class ScoreResponse(BaseModel):
    score:   int
    level:   str
    signals: dict
    factors: list[str]


@app.post("/score", response_model=ScoreResponse)
def score(body: ScoreRequest):
    """
    Evaluate risk for an incoming access request.
    Called by the policy engine before every authorization decision.
    """
    result = calculate_risk(
        user_id=body.user_id,
        username=body.username,
        ip_address=body.ip_address,
        user_agent=body.user_agent,
    )
    return ScoreResponse(**result)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "risk-engine"}
