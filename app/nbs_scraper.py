import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Optional

BASE = "https://nbs.rs"

async def fetch_belibor() -> Dict[str, List[Dict[str, Optional[str]]]]:
    """Scrape the BELIBOR / daily rates table and return structured data.

    Returns a dict with keys: date (str if present) and rows (list of {"tenor":..., "values":[...]})
    """
    url = urljoin(BASE, "/sr/finansijsko_trziste/dnevni-pregled-kamatnih-stopa")
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

    # Find the first responsive table (observed on the site)
    table = soup.find("table", class_="responsive-table")
    rows = []
    if table:
        tbody = table.find("tbody") or table
        for tr in tbody.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"]) ]
            if not cells:
                continue
            tenor = cells[0]
            values = cells[1:]
            rows.append({"tenor": tenor, "values": values})

    # Try to extract a date from the page (input#Date or similar)
    date_input = soup.find("input", id="Date")
    date = date_input["value"] if date_input and date_input.has_attr("value") else None

    return {"source": "nbs", "page": url, "date": date, "rows": rows}


async def fetch_latest_ioi_pdf() -> Optional[str]:
    """Find and return an absolute URL to the latest IOI (Inflation Report) PDF, if present."""
    url = urljoin(BASE, "/sr_RS/drugi-nivo-navigacije/publikacije-i-istrazivanja/IOI/")
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

    # Find links that look like PDFs in the IOI listing
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            pdf_links.append(urljoin(BASE, href))

    # Return the first PDF (page usually lists latest first) or None
    return pdf_links[0] if pdf_links else None


# Simple synchronous wrapper helpers for convenience (call from sync code)
def fetch_belibor_sync():
    import asyncio
    return asyncio.run(fetch_belibor())


def fetch_latest_ioi_pdf_sync():
    import asyncio
    return asyncio.run(fetch_latest_ioi_pdf())
