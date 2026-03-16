import asyncio
from scrapers.ab import AbScraper
from scrapers.sklavenitis import SklavenitisScraper
from scrapers.galaxias import GalaxiasScarper
import time

async def main():
    scraper = GalaxiasScarper()
    products = []
    start = time.perf_counter()
    async for product in scraper.fetch_products():
        products.append(product)
    print(f"Scraped {len(products)} products in {time.perf_counter()-start} seconds!")

if __name__ == "__main__":
    asyncio.run(main())
