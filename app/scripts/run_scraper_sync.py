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


if __name__ == '__main__':
    bel = fetch_belibor_sync()
    ioi = fetch_latest_ioi_pdf_sync()
    out = {'belibor': bel, 'latest_ioi_pdf': ioi}
    with open('nbs_scrape_output.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('WROTE nbs_scrape_output.json')
