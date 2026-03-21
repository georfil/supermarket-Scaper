import asyncio
from scrapers import AbScraper, SklavenitisScraper, GalaxiasScraper, MyMarketScraper
from pipeline import run_all_scrapers, clean_products
import pandas as pd
from models.product import Product


SCRAPERS = [
    AbScraper(),
    SklavenitisScraper(),
    GalaxiasScraper(),
    MyMarketScraper()
]


async def main():
    scraper_results = await run_all_scrapers(SCRAPERS)
    # scraper_results = pd.read_excel("testing/output.xlsx")
    # scraper_results = scraper_results.where(scraper_results.notna(), other=None)
    # scraper_results = [Product(**row) for row in scraper_results.to_dict(orient="records")]

    clean_results = clean_products(scraper_results)

    from db.repository import save_products

    save_products(clean_results)


if __name__ == "__main__":
    asyncio.run(main())
