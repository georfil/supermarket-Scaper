MERGE dbo.products AS target
USING staging.products AS source
    ON target.product_id = source.product_id
WHEN MATCHED THEN
    UPDATE SET
        target.original_product_code       = source.original_product_code,
        target.product_name                = source.product_name,
        target.brand                       = source.brand,
        target.supermarket_code            = source.supermarket_code,
        target.original_product_type_level1 = source.original_product_type_level1,
        target.original_product_type_level2 = source.original_product_type_level2,
        target.original_product_type_level3 = source.original_product_type_level3,
        target.unit                        = source.unit,
        target.product_url                 = source.product_url
WHEN NOT MATCHED BY TARGET THEN
    INSERT (
        product_id, original_product_code, product_name, brand,
        supermarket_code, original_product_type_level1, original_product_type_level2,
        original_product_type_level3, unit, product_url
    )
    VALUES (
        source.product_id, source.original_product_code, source.product_name, source.brand,
        source.supermarket_code, source.original_product_type_level1, source.original_product_type_level2,
        source.original_product_type_level3, source.unit, source.product_url
    );
