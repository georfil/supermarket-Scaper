from models import ProductToClassify, ProductType
from pipeline.categorise.prompt_builder import build_system_prompt, build_prompt
from utils.llm import call_llm, get_cost
import json
import logging

logger = logging.getLogger(__name__)

BATCH_SIZE = 30

JSON_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "categorisation",
        "schema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "type_code": {"type": "string"}
                        },
                        "required": ["id", "type_code"]
                    }
                }
            }
        }
    }
}

async def run_categorisation(products: list[ProductToClassify], productTypes: list[ProductType] ):
    system_prompt = build_system_prompt(productTypes)
    products = products[:50]
    results = []
    for i in range(0,len(products), BATCH_SIZE ):
        products_batch = products[i: i + BATCH_SIZE]
        prompt = build_prompt(products_batch)
        response = await call_llm(
                                prompt=prompt,
                                system_prompt=system_prompt,
                                temperature=0,
                                json_schema=JSON_SCHEMA)
        
        batch_results = json.loads(response.choices[0].message.content)['results']
        # print(f"Raw results: {batch_results}")
        # print(f"Sample codes in productTypes: {[pt.product_type_code for pt in productTypes[:5]]}")
        results.extend(batch_results)

        for result, product in zip(batch_results, products_batch):
            matched = next((pt for pt in productTypes if pt.product_type_code == str(result.get('type_code'))), None)
            print(f"{result.get('id')} | {product.name} | {product.original_category_level3} | {matched.product_type_level4}")

    print(f"\nTotal cost: ${get_cost():.4f}")
