from dataclasses import dataclass

@dataclass
class ProductType:
    """
    Class for product types
    
    """
    product_type_code: str
    product_type_level1: str
    product_type_level2: str
    product_type_level3: str
    product_type_level4: str