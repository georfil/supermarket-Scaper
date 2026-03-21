from scrapers.base import BaseScraper
from models.product import Product
import requests
from bs4 import BeautifulSoup
import json
import aiohttp
import asyncio
from utils.progress import track


class MyMarketScraper(BaseScraper):

    def _fetch_categories(self) -> list[str]:
        """Fetches product categories of My Market
        
        Returns:
            List of urls, regarding product categories
        """
        url = "https://www.mymarket.gr/sitemap/categories-tree"
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        categories = list(filter(lambda x:"offer" not in x,[h2.a["href"] + "?perPage=100&page={}" for h2 in soup.find_all("h2") ]))
        return categories
    
    async def _fetch_products_of_category(self, category_url:str, session:aiohttp.ClientSession, sem: asyncio.Semaphore):
        page = 1
        products = []
        async with sem:
            while True:
                url = category_url.format(page)
                async with session.get(url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    products_of_page = [{
                        **json.loads(article["data-google-analytics-item-value"]),
                        **{"url":article.a.get("href", None)},
                        **{"price_per_unit":list(filter(lambda x: x != '' ,article.find("div", attrs={"class":"measurment-unit-row"}).text.strip().split("\n"))) }
                    }
                    for article in soup.find_all("article")]
                    if len(products_of_page) == 0:
                        return products
                    products.extend(products_of_page)
                    
                page +=1

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
    
    @track(desc="My Market", unit="product")
    async def fetch_products(self):
        categories = self._fetch_categories()
        sem = asyncio.Semaphore(10)

        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_products_of_category(cat, session, sem) for cat in categories]
            for coro in asyncio.as_completed(tasks):
                products_of_category = await coro
                for product in products_of_category:
                    yield self._parse_product(product)