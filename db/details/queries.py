from db.connection import get_connection
from models import ProductUrl

def get_products() -> list[ProductUrl]:

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, supermarket_code, url  FROM dbo.products WHERE searchedDetails = 0 ")
    rows = cursor.fetchall()
    conn.close()
    return [ProductUrl(
                product_id=row[0], 
                supermarket=row[1], 
                url=row[2]
            ) 
            for row in rows]



