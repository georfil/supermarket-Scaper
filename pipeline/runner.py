import time
import asyncio
import pandas as pd
from dataclasses import asdict
from models.product import Product

async def run_all_scrapers(SCRAPERS) -> list[Product]:
    products = []
    start = time.perf_counter()
    scraper_results = await asyncio.gather(*[run_scraper(scraper) for scraper in SCRAPERS])
    for results in scraper_results:
        for product in results:
            products.append(product)
    print(f"Scraped {len(products)} products in {time.perf_counter()-start:.2f} seconds!")


    _save_products(products)

    return products



async def run_scraper(scraper):
    return [product async for product in scraper.fetch_products()]



def _save_products(products: list[Product]) -> None:   
    df = pd.DataFrame([asdict(p) for p in products])
    df.to_excel("testing/output.xlsx", index=False)
    print("Saved successfully to excel!")

