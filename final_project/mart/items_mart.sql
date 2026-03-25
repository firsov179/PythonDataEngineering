CREATE TABLE IF NOT EXISTS dm_items AS
SELECT
    oi.order_id,
    o.user_id,
    o.store_id,
    i.item_id,
    i.item_title,
    i.item_category,
    DATE(o.created_at) AS order_date,
    EXTRACT(YEAR FROM o.created_at) AS year,
    EXTRACT(MONTH FROM o.created_at) AS month,
    EXTRACT(DAY FROM o.created_at) AS day,
    oi.item_quantity,
    oi.item_canceled_quantity,
    (oi.item_price * oi.item_quantity) - COALESCE(oi.item_discount, 0) AS item_turnover,
    (oi.item_canceled_quantity > 0) AS has_canceled
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN items i ON oi.item_id = i.item_id;

CREATE INDEX idx_dm_items_item_date 
ON dm_items (item_id, order_date);

CREATE INDEX idx_dm_items_category 
ON dm_items (item_category);

