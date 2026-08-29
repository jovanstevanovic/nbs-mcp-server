from .nbs_client import NBSClient

async def build_context(refresh: bool = False):
    client = NBSClient()
    try:
        exchange = await client.get_exchange()
        cpi = await client.get_cpi()
    finally:
        await client.close()

    envelope = {
        "source": "nbs",
        "exchange": exchange,
        "cpi": cpi,
    }
    return envelope
