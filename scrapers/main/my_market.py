from scrapers.main.base import BaseScraper
from models import Product
from typing import AsyncGenerator
from utils.http import fetch_text
from bs4 import BeautifulSoup
import json
import aiohttp
import asyncio
import logging


logger = logging.getLogger(__name__)

class MyMarketScraper(BaseScraper):

    async def _fetch_categories(self, session: aiohttp.ClientSession) -> list[str]:
        """Fetches product categories of My Market

        Returns:
            List of urls, regarding product categories
        """
        try:
            html = await fetch_text(session, "https://www.mymarket.gr/sitemap/categories-tree")
            soup = BeautifulSoup(html, 'html.parser')
            return list(filter(lambda x: "offer" not in x, [h2.a["href"] + "?perPage=100&page={}" for h2 in soup.find_all("h2")]))
        except (AttributeError, TypeError):
            logger.exception("Unexpected structure when fetching categories")
            raise
    
    async def _fetch_products_of_category(self, category_url: str, session: aiohttp.ClientSession) -> list[dict]:
        page = 1
        products = []
        while True:
            url = category_url.format(page)
            try:
                async with self.sem:
                    html = await fetch_text(session, url)
            except aiohttp.ClientResponseError as e:
                if e.status == 404: #No more pages , returns a 404 error
                    break
                raise
            try:
                soup = BeautifulSoup(html, 'html.parser')
                products_of_page = [{
                    **json.loads(article["data-google-analytics-item-value"]),
                    **{"url":article.a.get("href", None)},
                    **{"price_per_unit":list(filter(lambda x: x != '' ,article.find("div", attrs={"class":"measurment-unit-row"}).text.strip().split("\n"))) }
                }
                for article in soup.find_all("article")]
                if len(products_of_page) == 0:
                    break
                products.extend(products_of_page)
            except Exception:
                logger.exception("Error parsing products from %s", url)
                continue

            page += 1

        return products

    def _parse_product(self, product: dict)-> Product:
        #contains both price per unit and unit in the form of a list``
        if 2 <= len(product['price_per_unit']) <= 4: 
            price_per_unit_combo =  product["price_per_unit"][2:] if len(product["price_per_unit"]) > 2 else product["price_per_unit"]
            price_per_unit = price_per_unit_combo[0][:-1].replace(".","").replace(",",".")
            unit = price_per_unit_combo[1] if len(price_per_unit_combo) == 2 else ''
        else:
            price_per_unit = ''
            unit = ''
            
        return Product(
            product_id= product["id"],
            title= product["name"],
            brand= product["brand"],
            supermarket= "my_market",
            price= product["price"],
            price_per_unit= float(price_per_unit) if price_per_unit !='' else None,
            unit= unit,
            url= product["url"]
        )
    
    async def fetch_products(self) -> AsyncGenerator[Product, None]:
        async with aiohttp.ClientSession() as session:
            categories = await self._fetch_categories(session)
            tasks = [self._fetch_products_of_category(cat, session) for cat in categories]
            for coro in asyncio.as_completed(tasks):
                products_of_category = await coro
                for product in products_of_category:
                    try:
                        yield self._parse_product(product)
                    except Exception:
                        logger.exception("Failed to parse product, skipping: %s", product)