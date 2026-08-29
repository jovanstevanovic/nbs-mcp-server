import asyncio
from app.mcp import build_context

import pytest

@pytest.mark.asyncio
async def test_build_context_returns_envelope():
    envelope = await build_context()
    assert isinstance(envelope, dict)
    assert "source" in envelope
