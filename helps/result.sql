SELECT
    main.uuid AS uuid,
    main.title AS title,
    s.uuid AS similar_uuid,
    s.title AS similar_title,
    s.description AS similar_description
FROM
    sku AS main
JOIN
    sku AS s ON s.uuid = ANY(main.similar_sku)
WHERE
    main.similar_sku <> '{}'::uuid[]  -- Условие для проверки непустого массива
AND
    main.uuid IN (
        SELECT uuid
        FROM sku
        WHERE similar_sku <> '{}'::uuid[]  -- Условие для проверки непустого массива
        LIMIT 5
    );