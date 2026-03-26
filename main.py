import asyncio
from config import setup_logging
from scrapers.main import *
from pipeline.main import run_all_scrapers, clean_products
from db.main import run_db_pipeline

setup_logging()


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

    if not clean_results:
        return

    run_db_pipeline(clean_results)


if __name__ == "__main__":
    asyncio.run(main())
