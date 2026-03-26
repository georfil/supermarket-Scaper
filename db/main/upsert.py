import logging
from pyodbc import Connection
from config.settings import SQL_DIR

logger = logging.getLogger(__name__)


def _load_sql(filename: str) -> str:
    return (SQL_DIR / filename).read_text()


def upsert_to_main(conn: Connection) -> None:
    """Merges staging data into dbo tables, then truncates staging on success."""
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(_load_sql("upsert_products.sql"))
        cursor.execute(_load_sql("upsert_prices.sql"))
        conn.commit()
        logger.info("Upsert completed successfully")
        cursor.execute("TRUNCATE TABLE staging.products")
        cursor.execute("TRUNCATE TABLE staging.productPrices")
        conn.commit()
    except Exception:
        cursor.execute("ROLLBACK")
        logger.exception("Upsert to main tables failed, transaction rolled back")
        raise