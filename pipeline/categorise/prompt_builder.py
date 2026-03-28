from models import ProductType, ProductToClassify


def build_system_prompt(categories: list[ProductType]) -> str:
    system_prompt = f"""
## Role

You are a supermarket taxonomy expert who specialises in categorising products.

## Context

You are a part of a project which involves scraping data from greek supermarkets and classifying them into categories

## Task

- You will be given supermarket products along with their original categories, exactly as they were scraped from ther site. 
- You will return the closest category you can match from the availiable options. I am looking for the code of the category
- If a match is not clear return None

**Limitations**
- You MUST select exactly one category code from the provided table.

**Undestand the product**
The key is to undestand what the product is. In order to undestand the product you are given, **focus on its name**. Use its original categorisation as context **only**.

## Format

Your output will be in JSON format

## Availiable Categories to choose from
{'\n'.join([f"code: {row.product_type_code} | **{row.product_type_level4}** ({row.product_type_level3})" for row in categories])}


## Examples

User: product_id: 1243 | Φρέσκο Γάλα Πλήρες 3,7% Λιπαρά 1 lt : Γαλακτοκομικά, Φυτικά Ροφήματα & Είδη Ψυγείου > Γάλα & Φυτικά Ροφήματα > Φρέσκο γάλα
Output: {{
    "id":423,
    "type_code": 115
}}

User: product_id: 4531 | Τριμμένο Τυρί Mozzarella 200g : Τυριά,Φυτικά Αναπληρώματα & Αλλαντικά > Τυριά > Τριμμένα τυριά
Output: {{
    "id":4531,
    "type_code": 576
}}



"""
    return system_prompt


def build_prompt(products: list[ProductToClassify]) -> str:
    return f"""
## Products to Categorise
{'\n'.join([f"product_id: {row.product_id} | {row.name} : {row.original_category_level1} > {row.original_category_level2} > {row.original_category_level3}" for row in products])}

"""