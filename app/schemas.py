from pydantic import BaseModel
from typing import Any

class MCPEnvelope(BaseModel):
    source: str
    exchange: Any
    cpi: Any
