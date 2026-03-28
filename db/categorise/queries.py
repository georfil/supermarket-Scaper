from db.connection import get_connection
from models import ProductToClassify, ProductType
import logging

logger = logging.getLogger(__name__)

def get_products_for_categorisation() -> list[ProductToClassify]:
    """
    Fetches all the products that should be classified by the llm
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, product_name, original_product_type_level1, original_product_type_level2, original_product_type_level3  FROM dbo.products WHERE product_type_code is NULL ")
    rows = cursor.fetchall()
    logger.info("Fetched %s products for classification.", len(rows))
    conn.close()
    return [ProductToClassify(
                product_id=row[0], 
                name = row[1],
                original_category_level1 =row[2], 
                original_category_level2 =row[3],
                original_category_level3 = row[4]
            ) 
            for row in rows]

def get_categories() -> list[ProductType]:
    """
    Fetches all the categories for the llm to classify into
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, product_type_level1, product_type_level2, product_type_level3, product_type_level4  FROM dbo.productTypes ")
    rows = cursor.fetchall()
    logger.info("Fetched %s categories for classification.", len(rows))
    conn.close()
    return [ProductType(
                product_type_code = row[0], 
                product_type_level1 =row[1], 
                product_type_level2 =row[2],
                product_type_level3 = row[3],
                product_type_level4 = row[4]
            ) 
            for row in rows]




