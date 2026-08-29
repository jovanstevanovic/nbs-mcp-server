import json
from app import nbs_scraper


def main():
    bel = nbs_scraper.fetch_belibor_sync()
    ioi = nbs_scraper.fetch_latest_ioi_pdf_sync()
    out = {"belibor": bel, "latest_ioi_pdf": ioi}
    with open('nbs_scrape_output.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('WROTE nbs_scrape_output.json')


if __name__ == '__main__':
    main()
