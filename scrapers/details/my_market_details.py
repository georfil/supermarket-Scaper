from scrapers.details.base_details import BaseScraperDetails
import aiohttp
import asyncio
import logging
from models import Product


class MyMarketScraperDetails(BaseScraperDetails):

    def __init__(self) -> None:
        super().__init__()

    async def fetch_product_details(self, products: list[Product]):
        pass

    