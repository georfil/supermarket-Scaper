from scrapers.base import BaseScraper
from models.product import Product
import asyncio
import aiohttp
import requests
from utils.progress import track

class GalaxiasScraper(BaseScraper):

    def __init__(self):
        self.url = "https://galaxias.shop/api/graphql"
        self.headers = {
            "cookie": "Path=%2F",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://galaxias.shop/eshop/59",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36"
        }


    def getBrands(self) -> dict:
        """Fetches all brands of Galaxias

        Returns:
            A dict with brand_id - brand_name 
        
        """
        query = """
        {
        categoryList(filters: {ids: {eq: ""}}) {
            attribute_filters
        }
        products(
            filter: {category_id: {eq: ""}}
            pageSize: 100
            currentPage: 1
            sort: {keyvoto_final_score: DESC}
        ) {
            total_count
            aggregations {
            attribute_code
            label
            options {
                label
                value
            }
            }
        }
        }
        """

        querystring = {"query": query}
        brands = {}
        
        response = requests.get(url = self.url, headers = self.headers, params =querystring) 
        data =  response.json()
        aggregations = data['data']['products']['aggregations']
        for aggregation_type in aggregations:
            if aggregation_type['attribute_code'] == 'keyvoto_brand':
                brands = {option['value']:option["label"] for option in aggregation_type['options']}
                return brands
                    
        return brands

    def _fetch_total_pages(self) -> int:
        query = """
        {
        categoryList(filters: {ids: {eq: "59"}}) {
            uid
        }
        products(
            filter: {
            keyvoto_brand: {in: []}
            }
            pageSize: 100
            currentPage: 1
            sort: {keyvoto_final_score: DESC}
        ) {
            items {
            sku
            name
            keyvoto_brand
            unit_measurement
            cost_per_unit
            price_range {
                minimum_price {
                final_price { value }
                regular_price { value }
                discount { amount_off percent_off }
                }
            }
            }
            page_info {
            page_size
            total_pages
            current_page
            }
            total_count
        }
        }
        """

        querystring = {"query":query}
        response = requests.get(url=self.url, headers=self.headers, params= querystring) 
        data = response.json()
        return data['data']['products']['page_info']['total_pages']
            

    async def _fetch_page(self, session:aiohttp.ClientSession, page:int, sem : asyncio.Semaphore):
        query = """
        {
        categoryList(filters: {ids: {eq: "59"}}) {
            uid
        }
        products(
            filter: {
            keyvoto_brand: {in: []}
            }
            pageSize: 100
            currentPage: """ + str(page) + """
            sort: {keyvoto_final_score: DESC}
        ) {
            items {
            sku
            name
            keyvoto_brand
            unit_measurement
            cost_per_unit
            price_range {
                minimum_price {
                final_price { value }
                regular_price { value }
                discount { amount_off percent_off }
                }
            }
            }
            page_info {
            page_size
            total_pages
            current_page
            }
            total_count
        }
        }
        """

        querystring = {"query":query}
        async with sem:
            async with session.get(url=self.url, headers=self.headers, params= querystring) as response:
                data = await response.json()
                return data['data']['products']['items']



    def _parse_product(self, product: dict, brands:dict) -> Product:
        return Product(
            product_id=product['sku'],
            title = product['name'],
            brand = brands.get(product['keyvoto_brand'], None),
            supermarket = "galaxias",
            price = product['price_range']['minimum_price']['final_price']['value'],
            price_per_unit = product['cost_per_unit'],
            unit = product['unit_measurement'],
            url = "https://galaxias.shop/product/"+ product['sku'],
        )
    
    @track(desc="Galaxias", unit="product")
    async def fetch_products(self):
        brands = self.getBrands()

        sem = asyncio.Semaphore(10)
        async with aiohttp.ClientSession() as session:

        
            total_pages = self._fetch_total_pages()

            tasks = [self._fetch_page(session, page, sem) for page in range(1, total_pages + 1)]
            for coro in asyncio.as_completed(tasks):
                product_page = await coro
                for product in product_page:
                    yield self._parse_product(product, brands)
            
    
