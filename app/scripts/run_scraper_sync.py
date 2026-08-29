import json
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = 'https://nbs.rs'


def fetch_belibor_sync():
    url = urljoin(BASE, '/sr/finansijsko_trziste/dnevni-pregled-kamatnih-stopa')
    try:
        r = httpx.get(url, timeout=20.0)
        r.raise_for_status()
    except Exception as e:
        print('ERROR_FETCH_BELIBOR', e)
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table', class_='responsive-table')
    rows = []
    if table:
        tbody = table.find('tbody') or table
        for tr in tbody.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['td','th'])]
            if cells:
                rows.append({'tenor': cells[0], 'values': cells[1:]})
    date_input = soup.find('input', id='Date')
    date = date_input['value'] if date_input and date_input.has_attr('value') else None
    return {'source': 'nbs', 'page': url, 'date': date, 'rows': rows}


def fetch_latest_ioi_pdf_sync():
    url = urljoin(BASE, '/sr_RS/drugi-nivo-navigacije/publikacije-i-istrazivanja/IOI/')
    try:
        r = httpx.get(url, timeout=20.0)
        r.raise_for_status()
    except Exception as e:
        print('ERROR_FETCH_IOI', e)
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    pdf_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            pdf_links.append(urljoin(BASE, href))
    return pdf_links[0] if pdf_links else None


def _get(url, **kw):
    headers = kw.pop('headers', {})
    headers.setdefault('User-Agent', 'nbs-mcp-scraper/1.0 (+https://github.com/jovanstevanovic/nbs-mcp-server)')
    try:
        return httpx.get(url, timeout=20.0, follow_redirects=True, headers=headers, **kw)
    except Exception as e:
        raise


def _find_link_by_keywords(soup, keywords):
    for a in soup.find_all('a', href=True):
        txt = (a.get_text(separator=' ', strip=True) or '') + ' ' + a['href']
        lower = txt.lower()
        for kw in keywords:
            if kw in lower:
                return a['href']
    return None


def fetch_exchange_rates_sync():
    # Try searching homepage for likely exchange-related links
    try:
        r = _get(BASE)
        r.raise_for_status()
    except Exception as e:
        print('ERROR_FETCH_EXCHANGE_HOME', e)
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    keywords = ['kurs', 'exchange', 'deviz', 'kursevi', 'kursna']
    link = _find_link_by_keywords(soup, keywords)
    if link:
        url = urljoin(BASE, link)
    else:
        # common fallback paths
        url = urljoin(BASE, '/en/finansijsko_trziste')
    try:
        r = _get(url)
        r.raise_for_status()
    except Exception as e:
        print('ERROR_FETCH_EXCHANGE', e)
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    tables = soup.find_all('table')
    rates = []
    for table in tables:
        # simple heuristic: find rows with at least 2-3 cells and numeric-looking values
        for tr in table.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['td','th'])]
            if len(cells) >= 2:
                rates.append(cells)
        if rates:
            break
    return {'source': url, 'rows': rates}


def fetch_cpi_sync():
    try:
        r = _get(BASE)
        r.raise_for_status()
    except Exception as e:
        print('ERROR_FETCH_CPI_HOME', e)
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    keywords = ['inflacija', 'inflation', 'cpi', 'indeks', 'potro']
    link = _find_link_by_keywords(soup, keywords)
    if link:
        url = urljoin(BASE, link)
    else:
        url = urljoin(BASE, '/en/publikacije')
    try:
        r = _get(url)
        r.raise_for_status()
    except Exception as e:
        print('ERROR_FETCH_CPI', e)
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    # look for tables or PDF links
    table = soup.find('table')
    if table:
        rows = []
        for tr in table.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['td','th'])]
            if cells:
                rows.append(cells)
        return {'source': url, 'rows': rows}
    # fallback: find PDFs mentioning inflation
    for a in soup.find_all('a', href=True):
        txt = a.get_text(separator=' ', strip=True).lower()
        if 'infl' in txt or 'cpi' in txt or 'indeks' in txt:
            return urljoin(BASE, a['href'])
    return None


if __name__ == '__main__':
    bel = fetch_belibor_sync()
    exchange = fetch_exchange_rates_sync()
    cpi = fetch_cpi_sync()
    ioi = fetch_latest_ioi_pdf_sync()
    out = {'belibor': bel, 'exchange_rates': exchange, 'cpi': cpi, 'latest_ioi_pdf': ioi}
    with open('nbs_scrape_output.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('WROTE nbs_scrape_output.json')
