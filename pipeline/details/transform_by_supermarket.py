from models import ProductUrl


def transform_by_supermarket(productUrls:list[ProductUrl], supermarkets) -> dict[str,list[str]]:
    
    products_dict = {supermarket : [] for supermarket in supermarkets}
    for productUrl in productUrls:
        products_dict[productUrl.supermarket].append(productUrl.url)
    return products_dict