import time
import asyncio
from models.product import Product
import logging
from scrapers.main.base import BaseScraper


logger = logging.getLogger(__name__)

async def run_all_scrapers(SCRAPERS: list[BaseScraper]) -> list[Product]:
    """Runs all scrapers concurrently"""

    products = []
    start = time.perf_counter()

    logger.info("Starting %d scrapers...", len(SCRAPERS))

    try:
        scraper_results = await asyncio.gather(
            *[run_scraper(scraper) for scraper in SCRAPERS],
            return_exceptions=True  # Don't let one failure kill the rest
        )
    except Exception:
        logger.exception("Unexpected error during asyncio.gather for scrapers")

    for scraper, results in zip(SCRAPERS, scraper_results):
        scraper_name = scraper.__class__.__name__
        if isinstance(results, Exception):
            logger.error("Scraper %s failed: %s", scraper_name, results)
            continue
        logger.info("Scraper %s returned %d products", scraper_name, len(results))
        products.extend(results)


    elapsed = time.perf_counter() - start
    logger.info("Scraped %d products in %.2fs", len(products), elapsed)

    return products



async def run_scraper(scraper: BaseScraper) -> list[Product] :
    """Runs an individual scraper of supermarket to retreive all the products"""
    scraper_name = scraper.__class__.__name__
    logger.debug("Starting scraper: %s", scraper_name)
    try:
        results = [product async for product in scraper.fetch_products()]
        logger.debug("Scraper %s finished with %d products", scraper_name, len(results))
        return results
    except Exception:
        logger.exception("Scraper %s raised an exception", scraper_name)
        raise


