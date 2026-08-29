from fastapi import FastAPI, HTTPException, Depends
from .mcp import build_context
from .schemas import MCPEnvelope

app = FastAPI(title="nbs-mcp-server")

@app.get('/mcp/status')
async def status():
    return {"status": "ok"}

@app.get('/mcp/context', response_model=MCPEnvelope)
async def get_context():
    envelope = await build_context()
    return envelope

@app.post('/mcp/refresh')
async def refresh(admin_key: str | None = None):
    # simple admin check - use ADMIN_API_KEY in production
    if admin_key is None:
        raise HTTPException(status_code=401, detail="admin key required")
    await build_context(refresh=True)
    return {"refreshed": True}
