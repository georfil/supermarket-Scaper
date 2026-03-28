import os
from pathlib import Path
import pyodbc
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
SQL_DIR = ROOT_DIR / "sql"

load_dotenv()

DB_SERVER   = os.environ["DB_SERVER"]
DB_DATABASE = os.environ["DB_DATABASE"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]


def pick_driver() -> str:
    available = pyodbc.drivers()
    for d in ("ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server", "SQL Server"):
        if d in available:
            return d
    raise RuntimeError(f"No SQL Server ODBC driver found. Available: {available}")


DB_URL = (
    f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_DATABASE}"
    f"?driver={pick_driver().replace(' ', '+')}"
)

LLM_MODEL = "gpt-4o-mini"


