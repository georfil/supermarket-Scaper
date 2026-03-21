import pandas as pd
from models.product import Product
from dataclasses import asdict
from utils.progress import track

UNIT_MAP = {
    "τεμ": "τεμάχιο",
    "λιτ": "λίτρο",
    "κιλ": "κιλό",
    "μεζ": "μεζούρα",
    "μ2": "τ.μ.",
    "/τεμ.": "τεμάχιο",
    "/κιλό": "κιλό",
    "/συσκ.": "τεμάχιο",
    "Λίτρο": "λίτρο",
    "Κιλό": "κιλό",
    "Τεμάχιο": "τεμάχιο",
    "Μεζούρα": "μεζούρα",
    "Μέτρο": "μέτρο",
    "Τιμή κιλού": "κιλό",
    "Τελική τιμή κιλού": "κιλό",
    "Τιμή τεμαχίου": "τεμάχιο",
    "Τιμή λίτρου": "λίτρο",
    "Τελική τιμή λίτρου": "λίτρο",
    "Τιμή μεζούρας": "μεζούρα",
    "Τελική τιμή τεμαχίου": "τεμάχιο",
    "Τιμή μέτρου": "μέτρο",
    "Τιμή ζεύγους": "τεμάχιο",
    "Τελική τιμή": "τεμάχιο",
    "Τιμή φύλλου": "τεμάχιο",
    "Τιμή τ.μ.": "τ.μ.",
    "κιλό" : "κιλό",
    "δόση": "μεζούρα",
    "λίτρο" : "λίτρο",
    "πλύση" : "μεζόυρα",
    "τεμ." : "τεμάχιο",
    "τ.μ." : "τ.μ.",
}

@track(desc="Cleaning", unit="product")
def clean_products(products: list[Product]) -> list[Product]:
    cleaned_products = []
    for product in products:
        if product.supermarket == "sklavenitis":
            if "€/" in product.price_per_unit:
                price_per_unit, unit = (product.price_per_unit.split(" €/"))
                product.price_per_unit = price_per_unit.strip().replace(".","").replace(",",".")
                product.unit = unit.strip()

        product.unit = UNIT_MAP.get(product.unit, None)
        product.unique_product_id = product.supermarket + product.product_id
        product.price = float(product.price) if product.price  else None
        product.price_per_unit = float(product.price_per_unit) if product.price_per_unit else None
        cleaned_products.append(product)

    _save_products(cleaned_products)
    return cleaned_products


def _save_products(products:pd.DataFrame) -> None:   

    df = pd.DataFrame([asdict(p) for p in products])
    df.to_excel("testing/output_clean.xlsx", index=False)
    print("Saved successfully to excel!  -  Clean")

