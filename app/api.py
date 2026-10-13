from fastapi import FastAPI, HTTPException
from app.schemas import ResearchRequest
from app.research import run_research
from app.providers.exa_provider import ProviderError

app = FastAPI(title="GTM Intelligence Explorer API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/research")
def research(request: ResearchRequest):
    try:
        return {"results": [p.model_dump() for p in run_research(request)]}
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Research failed ({exc.__class__.__name__}).") from exc
