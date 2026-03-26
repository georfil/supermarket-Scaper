import logging
from time import sleep
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from config.settings import DB_URL

logger = logging.getLogger(__name__)


def _create_engine_with_retry(max_retries: int = 3, base_delay: int = 5):
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Connecting to DB (attempt %d/%d)...", attempt, max_retries)
            engine = create_engine(DB_URL, fast_executemany=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established")
            return engine
        except OperationalError:
            if attempt == max_retries:
                logger.error("DB did not wake up after %d attempts", max_retries)
                raise RuntimeError("DB did not wake up in time")
            logger.warning("Database is waking up, retrying in %ds...", base_delay * attempt)
            sleep(base_delay * attempt)

def get_connection():
    
    engine = _create_engine_with_retry()
    if engine:
        return engine.raw_connection()
    else:
        return None