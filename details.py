from scrapers.details import *
from pipeline.details import transform_by_supermarket
from db.details import get_products
import asyncio

SCRAPER_DETAILS_DICT = {
    "ab" : AbScraperDetails,
    "sklavenitis": SklavenitisScraperDetails,
    "galaxias" : GalaxiasScraperDetails,
    "my_market" : MyMarketScraperDetails
}

async def main():
    products_to_scrape = get_products()
    products_by_supermarket = transform_by_supermarket(productUrls=products_to_scrape, supermarkets=SCRAPER_DETAILS_DICT.keys())

if __name__ == "__main__":
    asyncio.run(main())