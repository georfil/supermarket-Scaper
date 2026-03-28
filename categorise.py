import asyncio
from config import setup_logging
from db.categorise import get_categories, get_products_for_categorisation
from pipeline.categorise import run_categorisation

setup_logging()

async def main():

    categories = get_categories()
    products = get_products_for_categorisation()

    await run_categorisation(products=products, productTypes=categories)


if __name__ == "__main__":
    asyncio.run(main())