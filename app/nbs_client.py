import httpx
import os

class NBSClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or os.getenv('NBS_BASE_URL', 'https://api.nbs.rs')
        self.api_key = api_key or os.getenv('NBS_API_KEY')
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def get_exchange(self):
        # placeholder: return sample data or call real endpoint
        # In production, call: await self._client.get('/exchange')
        return {"rates": []}

    async def get_cpi(self):
        return {"cpi": {}}

    async def close(self):
        await self._client.aclose()
