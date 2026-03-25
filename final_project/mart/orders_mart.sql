CREATE TABLE IF NOT EXISTS dm_orders AS
WITH order_finance AS (
    SELECT
        oi.order_id,
        -- Оборот (с учетом скидок на уровне товаров)
        SUM((oi.item_price * oi.item_quantity) - COALESCE(oi.item_discount, 0)) AS gross_amount,
        -- Отмененные позиции
        SUM(oi.item_canceled_quantity * oi.item_price) AS canceled_amount,
        -- Фактически оплачено (без отмененных единиц)
        SUM(
            (oi.item_quantity - COALESCE(oi.item_canceled_quantity, 0)) * oi.item_price
            - COALESCE(oi.item_discount, 0)
        ) AS paid_amount
    FROM order_items oi
    GROUP BY oi.order_id
),
driver_stats AS (
    SELECT
        od.order_id,
        COUNT(*) AS driver_count,
        MAX(CASE WHEN is_final THEN driver_id END) AS final_driver_id,
        SUM(delivery_cost) AS total_delivery_cost
    FROM order_drivers od
    GROUP BY od.order_id
)
SELECT
    o.order_id,
    o.user_id,
    o.store_id,
    a.address_text,
    -- Дата
    DATE(o.created_at) AS order_date,
    EXTRACT(YEAR FROM o.created_at) AS year,
    EXTRACT(MONTH FROM o.created_at) AS month,
    EXTRACT(DAY FROM o.created_at) AS day,
    -- Финансы
    f.gross_amount - COALESCE(o.order_discount, 0) AS turnover,         -- оборот
    f.paid_amount - COALESCE(o.order_discount, 0) AS revenue,           -- выручка
    (f.paid_amount - COALESCE(o.order_discount, 0)) 
        - COALESCE(d.total_delivery_cost, 0) AS profit,                 -- прибыль
    -- Флаги
    (o.delivered_at IS NOT NULL) AS is_delivered,
    (o.canceled_at IS NOT NULL) AS is_canceled,
    -- Типы отмен
    (o.canceled_at IS NOT NULL AND o.delivered_at IS NOT NULL) AS cancel_after_delivery,
    (o.order_cancellation_reason IN ('Ошибка приложения', 'Проблемы с оплатой')) 
        AS cancel_service_fault,
    -- Курьеры
    (d.driver_count > 1) AS has_driver_change,
    -- Для активных курьеров
    d.final_driver_id
FROM orders o
LEFT JOIN order_finance f ON o.order_id = f.order_id
LEFT JOIN driver_stats d ON o.order_id = d.order_id
LEFT JOIN addresses a ON o.address_id = a.address_id;

CREATE INDEX idx_dm_orders_date_store 
ON dm_orders (order_date, store_id);

CREATE INDEX idx_dm_orders_user 
ON dm_orders (user_id);