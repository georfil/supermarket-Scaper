from models.product import Product

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

def clean_products(products: list[Product]) -> list[Product]:
    cleaned_products = []
    seen_ids = set()

    for product in products:
        if product.product_id in seen_ids:
            continue  # skip duplicate, move to next product

        product.unit = UNIT_MAP.get(product.unit, None)
        product.unique_product_id = product.supermarket + product.product_id
        product.price = float(product.price) if product.price else None
        product.price_per_unit = float(product.price_per_unit) if product.price_per_unit else None

        seen_ids.add(product.product_id)
        cleaned_products.append(product)

    return cleaned_products

