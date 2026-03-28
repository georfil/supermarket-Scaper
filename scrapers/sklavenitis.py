from scrapers.base import BaseScraper
from models import Product
from typing import AsyncGenerator
from utils.http import fetch_text
from bs4 import BeautifulSoup, Tag
import aiohttp
from json import loads
import asyncio
import logging


logger = logging.getLogger(__name__)

class SklavenitisScraper(BaseScraper):


    async def _fetch_categories(self, session: aiohttp.ClientSession) -> list[dict]:
        """Fetches all category URLs from the Sklavenitis website.

        Returns:
            - category URL templates with a `{}` placeholder for the page number.
            - level 1 category name
            - level 2 category name
        """
        try:
            html = await fetch_text(session, "https://www.sklavenitis.gr/katigories")
            soup = BeautifulSoup(html, 'html.parser')
            categories = soup.find_all('div', attrs={'class': 'categories_item'})
            result = []
            for cat in categories:
                for li in cat.find_all("li"):
                    result.append({
                        "url":"https://www.sklavenitis.gr/" + li.a["href"] + '?pg={}',
                        "level1_name":cat.h3.text.strip(),
                        "level2_name":li.text.strip()
                    })
            return result
        except Exception:
            logger.exception("Couldn't get product categories.")
            raise
            


    def _parse_product(self, product: Tag, level1_name: str, level2_name:str) -> Product:
        """Parses a BeautifulSoup Tag into a Product object.

        Args:
            product: A BeautifulSoup Tag representing a single product HTML element.
            title: Title of page, which point to level 2 category of products

        Returns:
            A Product object with fields populated from the HTML.
        """
        data = loads(product.get('data-plugin-analyticsclickable'))
        js_string = data['calls'][0][0]
        json_str = js_string.split('.push(')[2].split(');')[0]
        event_data = loads(json_str)
        item = event_data['ecommerce']['items'][0]
        priceDivs = product.find('div', attrs = {'class':'priceKil'}).find_all('div')
        pricePerKilo = priceDivs[-1].text.strip() if len(priceDivs)>0 else product.find('div', attrs = {'class':'priceKil'}).text.strip()
        unit = product.find('div', attrs = {'class':'price'}).span.text.strip()

        if "€/" in pricePerKilo:
            pricePerKilo, unit = pricePerKilo.split(" €/")
            pricePerKilo = pricePerKilo.strip().replace(".", "").replace(",", ".")
            unit = unit.strip()

        return Product(
            product_id = loads(product['data-item'])['ProductSKU'],
            title = item['item_name'].strip(),
            brand = item['item_brand'].strip() if item.get('item_brand') else None,
            supermarket = "sklavenitis",
            price = float(item['price']),
            price_per_unit = pricePerKilo,
            unit = unit,
            url = "https://www.sklavenitis.gr/"+ product.a['href'],
            product_type_level_1 = level1_name,
            product_type_level_2 = level2_name,
            product_type_level_3 = item.get("item_category", None)
            
        )
    
    async def _fetch_category_mappings(self, session: aiohttp.ClientSession) -> None:
        url = "https://www.sklavenitis.gr/katigories"
        html = await fetch_text(session, url)
        soup = BeautifulSoup(html, 'html.parser')
        categories_mappings = {}
        for div in soup.find_all("div", attrs={"class":"categories_item"}):
            main_cat = div.h3.text.strip()

            for li in div.find_all("li"):
                categories_mappings[li.text.strip()]=main_cat

        self.categories_mappings = categories_mappings

    async def _fetch_category(self, session: aiohttp.ClientSession, category: dict) -> tuple[Tag, str, str]:
        """Fetches all pages for a product category of Sklavenitis

        Args:
            session: The aiohttp session
            category_url: The url of a category of products (eg https://www.sklavenitis.gr/[category]])

        Returns:
            A tuple of products in the form of beautiful soup tags and level1 cat name and level2 cat name
        """
        
        page = 1
        total_products = []
        category_url = category['url']
        level1 = category['level1_name']
        level2 = category['level2_name']


        try:
            while True:
                current_page_url = category_url.format(page)
                async with self.sem:
                    html = await fetch_text(session, current_page_url)
                soup = BeautifulSoup(html, 'html.parser')
                product_list = soup.find('div', attrs={'id':'productList'}).section.find_all('div', attrs={'class':'product'})
                if len(product_list) == 0:
                    break
                total_products.extend(product_list)
                page += 1
        except AttributeError:
            logger.exception("Error finding section of products. Stopping fetching more pages of this category")

        return total_products , level1, level2
        
        
    async def fetch_products(self) -> AsyncGenerator[Product, None]:
        """
        Fetches all products from Sklavenitis.
        """

        async with aiohttp.ClientSession() as session:
            await self._fetch_category_mappings(session)
            categories = await self._fetch_categories(session)
            tasks = [self._fetch_category(session, category) for category in categories]
            for coro in asyncio.as_completed(tasks):
                product_list_of_category, level1_name, level2_name  = await coro
                for product in product_list_of_category:
                    try:
                        yield self._parse_product(product, level1_name, level2_name)
                    except Exception:
                        logger.exception("Failed to parse product, skipping - %s", product)
                    
