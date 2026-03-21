from time import sleep
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from config.settings import DB_URL


def _create_engine_with_retry(max_retries: int = 3, base_delay: int = 5):
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Connecting to DB (attempt {attempt})...")
            engine = create_engine(DB_URL, fast_executemany=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection established")
            return engine
        except OperationalError:
            print("Database is waking up...")
            if attempt == max_retries:
                raise RuntimeError("DB did not wake up in time")
            sleep(base_delay * attempt)


engine = _create_engine_with_retry()
