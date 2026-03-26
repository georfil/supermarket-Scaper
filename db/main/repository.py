import logging
from pyodbc import Connection
from models.product import Product

logger = logging.getLogger(__name__)

PRODUCT_SQL = """
    INSERT INTO staging.products (
        product_id, original_product_code, product_name, brand,
        supermarket_code, original_product_type_level1, original_product_type_level2,
        original_product_type_level3, unit, product_url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

PRICE_SQL = """
    INSERT INTO staging.productPrices (
        product_id, price, pricePerKilo, priceDate
    ) VALUES (?, ?, ?, ?)
"""


def save_products(products: list[Product], conn: Connection) -> None:
    """Inserts all products and their prices into staging tables in batches of 1000."""
    product_rows = [
        (
            p.unique_product_id, p.product_id, p.title, p.brand,
            p.supermarket, p.product_type_level_1, p.product_type_level_2,
            p.product_type_level_3, p.unit, p.url,
        )
        for p in products
    ]
    price_rows = [
        (p.unique_product_id, p.price, p.price_per_unit, p.scraped_at)
        for p in products
    ]

    logger.info("Saving %d products to staging", len(products))
    cursor = conn.cursor()
    cursor.fast_executemany = True

    for i in range(0, len(product_rows), 1000):
        batch = product_rows[i:i + 1000]
        try:
            cursor.executemany(PRODUCT_SQL, batch)
        except Exception as e:
            logger.error("product_rows batch [%d:%d] failed: %s\n%s", i, i + 1000, e, batch)
            raise

    for i in range(0, len(price_rows), 1000):
        batch = price_rows[i:i + 1000]
        try:
            cursor.executemany(PRICE_SQL, batch)
        except Exception as e:
            logger.error("price_rows batch [%d:%d] failed: %s\n%s", i, i + 1000, e, batch)
            raise

    logger.info("Successfully saved %d products to staging", len(products))
