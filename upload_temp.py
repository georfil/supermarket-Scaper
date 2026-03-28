from db.connection import get_connection
import pandas as pd
conn = get_connection()
cursor = conn.cursor()
cursor.fast_executemany = True

SQL = """
    INSERT INTO dbo.productTypes (
        code, product_type_level1, product_type_level2, product_type_level3, product_type_level4
    ) VALUES (?, ?, ?, ?, ?)
"""

PATH = r"C:\Users\georf\Downloads\taxonomy_v4.xlsx"

df = pd.read_excel(PATH).reset_index()
ls = df.values.tolist()
cursor.executemany(SQL, ls)
conn.commit()
conn.close()