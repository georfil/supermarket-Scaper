MERGE dbo.productPrices AS target
USING staging.productPrices AS source
    ON target.product_id = source.product_id
    AND target.priceDate = source.priceDate
WHEN NOT MATCHED BY TARGET THEN
    INSERT (product_id, price, pricePerKilo, priceDate)
    VALUES (source.product_id, source.price, source.pricePerKilo, source.priceDate);
