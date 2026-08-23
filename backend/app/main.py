import os
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Optional Firebase Admin verification. Configure FIREBASE_SERVICE_ACCOUNT_JSON
# with a service-account JSON path to enforce real Google tokens server-side.
try:
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth
except Exception:
    firebase_admin = None
    credentials = None
    firebase_auth = None

app = FastAPI(title="BrandPulse Agent API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mission(BaseModel):
    objective: str
    industry: str
    audience: str
    competitors: List[str] = []
    brandContext: str = ""

class AuthUser(BaseModel):
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    provider: str = "demo"


def init_firebase():
    if not firebase_admin or firebase_admin._apps:
        return
    service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if service_account and os.path.exists(service_account):
        firebase_admin.initialize_app(credentials.Certificate(service_account))

init_firebase()


def get_current_user(authorization: Optional[str]) -> AuthUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Sign in required")
    token = authorization.split(" ", 1)[1]
    if token.startswith("demo-"):
        return AuthUser(uid=token, name="Demo User", provider="demo")
    if not firebase_auth or not firebase_admin or not firebase_admin._apps:
        raise HTTPException(status_code=401, detail="Firebase Admin is not configured on the backend")
    try:
        decoded = firebase_auth.verify_id_token(token)
        return AuthUser(uid=decoded["uid"], email=decoded.get("email"), name=decoded.get("name"), provider="google")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired Google session")

@app.get("/health")
def health():
    return {"status": "ok", "service": "brandpulse-backend"}

@app.get("/api/me")
def me(authorization: Optional[str] = Header(default=None)):
    user = get_current_user(authorization)
    return user.model_dump()

@app.post("/api/missions/run")
def run(m: Mission, authorization: Optional[str] = Header(default=None)):
    user = get_current_user(authorization)
    comps = m.competitors or ["Competitor A", "Competitor B", "Competitor C"]
    sources = [
      {"source": f"{comps[0]} — website", "type": "URL", "signal": "Heavy emphasis on convenience and speed of delivery.", "interp": "Messaging appears heavily convenience-led.", "conf": 84},
      {"source": f"{comps[1] if len(comps)>1 else comps[0]} — social ads", "type": "Web", "signal": "Frequent discount and urgency-based creative.", "interp": "Positioning leans price-led, not trust-led.", "conf": 79},
      {"source": f"Industry report — {m.industry}", "type": "PDF", "signal": "Rising demand for ingredient transparency.", "interp": "Audience increasingly distrusts unverified claims.", "conf": 88},
      {"source": "Audience forum threads", "type": "Web", "signal": "Repeated complaints about vague marketing claims.", "interp": "Credibility gap exists across the category.", "conf": 81},
      {"source": f"{comps[2] if len(comps)>2 else comps[-1]} — brand guide", "type": "URL", "signal": "Visual identity emphasizes lifestyle over substance.", "interp": "Little competitor ownership of a credibility angle.", "conf": 76}
    ]
    positions=["premium efficacy","convenience-led access","price-led volume","community-led trust","clinical credibility"]
    strengths=["Strong paid distribution","High repeat purchase rate","Recognizable visual identity","Fast fulfillment network"]
    weaknesses=["Generic, undifferentiated messaging","Thin evidence behind claims","Weak retention content","Inconsistent brand voice"]
    messaging=["Convenience-first, feature-heavy copy","Aspirational lifestyle framing","Discount-driven urgency language","Clinical, ingredient-forward copy"]
    comps_data=[{"name":n,"positioning":positions[i%len(positions)],"strengths":strengths[i%len(strengths)],"weaknesses":weaknesses[(i+1)%len(weaknesses)],"messaging":messaging[i%len(messaging)]} for i,n in enumerate(comps)]
    hypothesis=f"A credibility-led positioning — built on transparent, evidence-backed claims — appears underserved among {', '.join(comps)} for {m.audience}."
    return {
      "user": user.model_dump(), "objective":m.objective,"industry":m.industry,"audience":m.audience,"brandContext":m.brandContext,
      "comps":comps_data,"sources":sources,"hypothesis":hypothesis,"confidence":87,
      "memory":["Brand voice: "+(m.brandContext or "Professional, concise, human."), "Audience persona: "+m.audience, "Educational content outperformed promotional content in the last campaign."],
      "strategy":["Lead with credibility-led, evidence-backed positioning.","Publish transparent proof and useful educational content.","Build a recurring proof loop from research, customer outcomes and product evidence."],
      "trace":["PLANNER","WEB RESEARCH","URL ANALYZER","MEMORY","COMPETITIVE ANALYSIS","AUDIENCE ANALYST","OPPORTUNITY DETECTION","STRATEGIST","CONTENT AGENT","CRITIC","AUTONOMOUS REVISION","FINAL"]
    }
