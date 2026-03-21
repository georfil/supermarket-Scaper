from scrapers.base import BaseScraper
from typing import AsyncGenerator
from models.product import Product
from json import dumps
import aiohttp
import asyncio
from utils.progress import track

class AbScraper(BaseScraper):

    def __init__(self):
        self.url = "https://www.ab.gr/api/v1/"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
            "x-apollo-operation-id": "841bc048e809cf7f460d0473995516d39464c46b70952bd8b26235f881f571b5",
            "x-apollo-operation-name": "GetCategoryProductSearch",
            "x-default-gql-refresh-token-disabled": "true",
        }


    def _get_params(self, page: int) -> dict:
        """Builds the query parameters for the AB API request.

        Args:
            page: The page number to request.

        Returns:
            A dictionary of query parameters.
        """
        return {
                "operationName": "GetCategoryProductSearch",
                "variables": dumps({"pageNumber":page,"pageSize":50,"plainChildCategories":True}, separators=(',', ':')),
                "extensions": dumps(
                {"persistedQuery":{"version":1,"sha256Hash":"afce78bc1a2f0fe85f8592403dd44fae5dd8dce455b6eeeb1fd6857cc61b00a2"}}
                , separators=(',', ':'))
            }
    
    def _parse_products(self, data: dict) -> list[Product]:
        """Parses raw API response into a list of Product objects.

        Args:
            data: The raw JSON response from the AB API.

        Returns:
            A list of Product objects, or an empty list if parsing fails.
        """

        try:
            products = data['data']['categoryProductSearch']['products']
        except TypeError:
            return []

        for product in products:
            price_per_unit = product.get("price", {}).get("supplementaryPriceLabel1", None).split(" ")

            yield Product(
                product_id = product.get("code", None),
                title = product.get("name", None),
                brand = product.get("manufacturerName", "ΑΒ"),
                supermarket = "ab",
                price = product.get("price", {}).get("value", None),
                price_per_unit = float(price_per_unit[0].replace(".","").replace(",",".")),
                unit = price_per_unit[2] if len(price_per_unit)>2 else None,
                url = "https://www.ab.gr" + product.get("url", None) if product.get("url", None) else None,
            ) 
      


    async def _fetch_page(self, session: aiohttp.ClientSession, page: int, sem: asyncio.Semaphore) -> dict:
        """Fetches a single page of products from the AB API.

        Args:
            session: The aiohttp client session to use for the request.
            page: The page number to fetch.
            sem: Semaphore to limit the number of concurrent requests.

        Returns:
            The raw JSON response as a dictionary.
        """
        async with sem:
            async with session.get(self.url, headers=self.headers, params=self._get_params(page)) as response:
                data = await response.json() 
                return data
            
    @track(desc="AB", unit="product")
    async def fetch_products(self) -> AsyncGenerator[Product, None]:
        """Fetches all products from the AB supermarket API concurrently.

        Yields:
            Product objects parsed from all pages.
        """
        sem = asyncio.Semaphore(10)

        async with aiohttp.ClientSession() as session:

            data = await self._fetch_page(session, 1, sem)
            for product in self._parse_products(data):
                yield product
            total_pages = data['data']['categoryProductSearch']['pagination']['totalPages']

            tasks = [self._fetch_page(session, page, sem) for page in range(2, total_pages + 1)]
            for coro in asyncio.as_completed(tasks):
                data = await coro
                for product in self._parse_products(data):
                    yield product
