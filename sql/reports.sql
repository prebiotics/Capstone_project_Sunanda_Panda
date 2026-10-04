SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;

UPDATE orders SET discount_pct = NULL WHERE discount_pct = '';
UPDATE orders SET rating = NULL WHERE rating = '';
-- =========================================================
--  a) Order totals
-- =========================================================

SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(o.quantity * p.price *(1 - COALESCE(o.discount_pct, 0) / 100.0)),2) AS total_revenue,
    ROUND(AVG(o.quantity * p.price *(1 - COALESCE(o.discount_pct, 0) / 100.0)),2) AS avg_order_value
FROM orders o
JOIN products p
    ON o.product_id = p.product_id;

-- =========================================================
-- b) COUNT(*) vs COUNT(rating)
-- =========================================================

SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS unrated_orders
FROM orders;

-- =========================================================
-- c) (1) Customers with zero orders - LEFT JOIN
-- =========================================================

SELECT
    c.customer_id,
    c.name
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.name
HAVING COUNT(o.order_id) = 0;

-- =========================================================
-- c) (2) Customers with zero orders - NOT IN
-- =========================================================

SELECT
    customer_id,
    name
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id
    FROM orders
);

-- =========================================================
-- d) RETURN RATE BY CITY
-- =========================================================

SELECT
    c.city,
    COUNT(*) AS total_orders,
    SUM(
        CASE
            WHEN o.returned = 1 THEN 1
            ELSE 0
        END
    ) AS returned_orders,
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN o.returned = 1 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        1
    ) AS return_rate_pct
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

-- =========================================================
-- e) TOP 5 CUSTOMERS BY SPEND
-- Tie-break: customer_id ASC makes ranking deterministic.
-- =========================================================

SELECT
    c.customer_id,
    c.name,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_spend
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.name
ORDER BY
    total_spend DESC,
        c.customer_id ASC
LIMIT 5;

-- =========================================================
-- e) RANKS 3-5
-- =========================================================

SELECT
    c.customer_id,
    c.name,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_spend
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.name
    ORDER BY
    total_spend DESC,
    c.customer_id ASC
LIMIT 3 OFFSET 2;

-- =========================================================
-- f) ORDER COUNT AND REVENUE BY CATEGORY
-- =========================================================

SELECT
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS category_revenue
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- =========================================================
-- g) CUSTOMERS WHOSE NAME STARTS WITH A
-- =========================================================

SELECT
    customer_id,
    name,
    city
FROM customers
WHERE name LIKE 'A%';

-- =========================================================
-- h) DISTINCT ACQUISITION SOURCES
-- =========================================================

SELECT DISTINCT
    acquisition_source
FROM customers
ORDER BY acquisition_source;

-- =========================================================
-- i) ADD LOYALTY TIER
-- =========================================================

ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier =
    CASE
        WHEN city_tier = 1 THEN 'Gold'
        ELSE 'Silver'
    END;
    
select * from customers;

-- Verify loyalty tiers

SELECT
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier;
