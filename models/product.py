from dataclasses import dataclass, field
from datetime import date

@dataclass
class Product:
    """
    Class for supermarket products
    
    """

    product_id: str
    title: str
    brand: str
    supermarket: str
    price: float
    price_per_unit: float
    unit: str
    url: str
    scraped_at: date = field(default_factory=date.today)
    weight: float | None = None
    product_type_level_1: str | None = None
    product_type_level_2: str | None = None
    product_type_level_3: str | None = None
    unique_product_id: str | None = None


    