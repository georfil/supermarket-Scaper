import asyncio
from scrapers import AbScraper, SklavenitisScraper, GalaxiasScraper, MyMarketScraper
from dataclasses import asdict
import time
import pandas as pd

SCRAPERS = [
    AbScraper(),
    # SklavenitisScraper(),
    # GalaxiasScraper(),
    # MyMarketScraper()
]


async def run_scraper(scraper):
    return [product async for product in scraper.fetch_products()]
 

async def main():
    products = []
    start = time.perf_counter()
    scraper_results = await asyncio.gather(*[run_scraper(scraper) for scraper in SCRAPERS])
    for results in scraper_results:
        for product in results:
            products.append(product)
    print(f"Scraped {len(products)} products in {time.perf_counter()-start:.2f} seconds!")

    df = pd.DataFrame([asdict(p) for p in products])
    df.to_excel("testing/output_ab.xlsx", index=False)

if __name__ == "__main__":
    asyncio.run(main())
