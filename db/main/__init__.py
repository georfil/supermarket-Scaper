from db.main.connection import get_connection
from db.main.upsert import upsert_to_main
from db.main.repository import save_products
from models.product import Product
import logging

logger = logging.getLogger(__name__)

def run_db_pipeline(products: list[Product]) -> None:
    """Runs the full DB pipeline: loads products into staging then merges to main tables."""
    conn = get_connection()
    try:
        save_products(products, conn)
        conn.commit()
        upsert_to_main(conn)
    except Exception:
        logger.exception("DB pipeline failed")
        raise
    finally:
        conn.close()