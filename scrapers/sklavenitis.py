from scrapers.base import BaseScraper
from models.product import Product
from typing import AsyncGenerator
from bs4 import BeautifulSoup, Tag
import aiohttp
from json import loads
import requests
import asyncio
from utils.progress import track

class SklavenitisScraper(BaseScraper):


    def _fetch_categories(self) -> list[str]:
        """Fetches all category URLs from the Sklavenitis website.

        Returns:
            A list of category URL templates with a `{}` placeholder for the page number.
        """
        url = "https://www.sklavenitis.gr/katigories"

        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        categories = soup.find_all('div', attrs={'class':'categories_item'})
        categories_url = ["https://www.sklavenitis.gr/" + cat.li.a["href"].split('/')[1] + '?pg={}' for cat in categories]
        return categories_url


    def _parse_product(self, product: Tag) -> Product:
        """Parses a BeautifulSoup Tag into a Product object.

        Args:
            product: A BeautifulSoup Tag representing a single product HTML element.

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

        return Product(
            product_id = loads(product['data-item'])['ProductSKU'],
            title = item['item_name'].strip(),
            brand = item['item_brand'].strip() if item.get('item_brand') else None,
            supermarket = "sklavenitis",
            price = float(item['price']),
            price_per_unit = pricePerKilo,
            unit = unit,
            url = "https://www.sklavenitis.gr/"+ product.a['href'],
        )
    

    async def _fetch_category(self, session:aiohttp.ClientSession, category_url: str, sem: asyncio.Semaphore) -> list[Tag]:
        """Fetches all pages for a product category of Sklavenitis

        Args:
            session: The aiohttp session
            category_url: The url of a category of products (eg https://www.sklavenitis.gr/[category]])
            sem: Semaphore to limit concurrent requests.

        Returns:
            A list of products in the form of beautiful soup tags
        """
        
        async with sem:
            page = 1
            total_products = []
            while True:
                current_page_url = category_url.format(page)
                async with session.get(current_page_url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    product_list = soup.find('div', attrs={'id':'productList'}).section.find_all('div', attrs={'class':'product'})
                    if len(product_list) == 0:                       
                        break
                    total_products.extend(product_list)              
                page +=1

            return total_products
        
    @track(desc="Sklavenitis", unit="product")
    async def fetch_products(self) -> AsyncGenerator[Product, None]:
        """
        Fetches all products from Sklavenitis.
        """

        sem = asyncio.Semaphore(10)

        categories_url = self._fetch_categories()
        async with aiohttp.ClientSession() as session:
            
            tasks = [self._fetch_category(session, category_url, sem) for category_url in categories_url]
            for coro in asyncio.as_completed(tasks):
                product_list_of_category = await coro
                for product in product_list_of_category:
                    yield self._parse_product(product)
                    
