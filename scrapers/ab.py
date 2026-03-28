from scrapers.base import BaseScraper
from typing import AsyncGenerator, Generator
from models import Product
from utils.http import fetch_json
from json import dumps
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)

class AbScraper(BaseScraper):

    def __init__(self) -> None:
        super().__init__()
        self.url = "https://www.ab.gr/api/v1/"
        self.main_headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
            "x-apollo-operation-id": "841bc048e809cf7f460d0473995516d39464c46b70952bd8b26235f881f571b5",
            "x-apollo-operation-name": "GetCategoryProductSearch",
            "x-default-gql-refresh-token-disabled": "true",
        }
        self.category_headers =  {
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
            "x-apollo-operation-id": "c79225574006df260367f8a15f40dd71adc6e9ea1fa30e30bc445c13fd2e96f5",
            "x-apollo-operation-name": "LeftHandNavigationBar",
            "x-default-gql-refresh-token-disabled": "true",
        }

    def _get_main_params(self, page: int) -> dict:
        """Builds the query parameters for the AB API request.

        Args:
            page: The page number to request.

        Returns:
            A dictionary of query parambeters.
        """
        return {
                "operationName": "GetCategoryProductSearch",
                "variables": dumps({"pageNumber":page,"pageSize":50,"plainChildCategories":True}, separators=(',', ':')),
                "extensions": dumps(
                {"persistedQuery":{"version":1,"sha256Hash":"189e7cb5a6ba93e55dc63e4eef0ad063ca3e8aedb0bdf2a58124e02d5d5d69a2"}}
                , separators=(',', ':'))
            }
    
    def _get_category_params(self) -> dict:
        """Builds the query parameters for the AB API request to retreive all categories.

        Returns:
            A dictionary of query parameters.
        """
        return  {
            "operationName": "LeftHandNavigationBar",
            "variables": dumps({"rootCategoryCode":"","cutOffLevel":"4","lang":"gr"}, separators=(',', ':')),
            "extensions": dumps(
            {"persistedQuery":{"version":1,"sha256Hash":"29a05b50daa7ab7686d28bf2340457e2a31e1a9e4d79db611fcee435536ee01c"}}
            , separators=(',', ':'))
        }
        

            
    async def _get_category_codes(self, session: aiohttp.ClientSession) -> dict[str, str]:
        """Parses the response from ab api and returns list of all categories

        Returns:
            {
            "url_greeklish_subset":"category_name"
            }
        """
        try:
            data = await self._fetch_categories(session)

            output = {}
            for main_cat in data['data']['leftHandNavigationBar']['levelInfo']:
                url = main_cat['url'].split("/c/")[0].split('/el/eshop/')[1]
                output[url] = main_cat['name']

            for level in data['data']['leftHandNavigationBar']['categoryTreeList']:
                categories = level['categoriesInfo']
                for cat in categories:
                    for subcat in cat['levelInfo']:
                        url = subcat['url'].split("/c/")[0].split('/el/eshop/')[1].split('/')[-1]
                        output[url] = subcat['name']

            logger.info("Fetched %d AB categories", len(output))
            return output
        except (KeyError, TypeError):
            logger.exception("Failed to parse AB category mapping")
            raise


    async def _fetch_categories(self, session: aiohttp.ClientSession) -> dict:
        """Fetches the full AB category tree."""
        async with self.sem:
            return await fetch_json(session, self.url, headers=self.category_headers, params=self._get_category_params())


    
    def _parse_products(self, data: dict) -> Generator[Product, None, None]:
        """Parses raw API response into a list of Product objects.

        Args:
            data: The raw JSON response from the AB API.

        Returns:
            A list of Product objects, or an empty list if parsing fails.
        """

        try:
            products = data['data']['categoryProductSearch']['products']
        except KeyError:
            logger.exception("Unexpected response structure from AB API: %s", data)
            return
        

        for product in products:
            try:
                price_per_unit_label = product.get("price", {}).get("supplementaryPriceLabel1") or ""
                price_per_unit = price_per_unit_label.split(" ")

                url = product.get("url", None) 
                subset_url = url.split("/p/")[0].split("/el/eshop/")[1].split("/")
                categories_parsed = {idx:self.category_mapping.get(subset, None) for idx, subset in enumerate(subset_url,1)}
                yield Product(
                    product_id = product.get("code", None),
                    title = product.get("name", None),
                    brand = product.get("manufacturerName", "ΑΒ"),
                    supermarket = "ab",
                    price = product.get("price", {}).get("value", None),
                    price_per_unit = float(price_per_unit[0].replace(".","").replace(",",".")),
                    unit = price_per_unit[2] if len(price_per_unit)>2 else None,
                    url = "https://www.ab.gr" + url,
                    product_type_level_1=categories_parsed.get(1, None),
                    product_type_level_2= categories_parsed.get(2, None),
                    product_type_level_3= categories_parsed.get(3, None)
                )
            except (KeyError, ValueError):
                logger.exception("Unexpected error occured in parsing this product: %s", product)

      


    async def _fetch_page(self, session: aiohttp.ClientSession, page: int) -> dict:
        """Fetches a single page of products from the AB API.

        Args:
            session: The aiohttp client session to use for the request.
            page: The page number to fetch.

        Returns:
            The raw JSON response as a dictionary.
        """
        async with self.sem:
            return await fetch_json(session, self.url, headers=self.main_headers, params=self._get_main_params(page))

    def _get_total_pages(self, data: dict) -> int:
        """Returns the total number of pages to fetch"""
        try:
            return data['data']['categoryProductSearch']['pagination']['totalPages']
        except KeyError:
            logger.exception("Unable to get total page number.")
            raise
            
    async def fetch_products(self) -> AsyncGenerator[Product, None]:
        """Fetches all products from the AB supermarket API concurrently.

        Yields:
            Product objects parsed from all pages.
        """
        async with aiohttp.ClientSession() as session:

            data = await self._fetch_page(session, 1)           

            total_pages = self._get_total_pages(data)
            self.category_dict = await self._get_category_codes(session)

            for product in self._parse_products(data):
                yield product

            tasks = [self._fetch_page(session, page) for page in range(2, total_pages + 1)]
            for coro in asyncio.as_completed(tasks):
                data = await coro
                for product in self._parse_products(data):
                    print(product)
                    yield product
