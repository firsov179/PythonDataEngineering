-- Оборот товара
SELECT item_id, SUM(item_turnover)
FROM dm_items
GROUP BY item_id;

-- Заказанные единицы
SELECT SUM(item_quantity) FROM dm_items;

-- Отмененные единицы
SELECT SUM(item_canceled_quantity) FROM dm_items;

-- Заказы с товаром
SELECT COUNT(DISTINCT order_id) FROM dm_items;

-- Заказы с отменой товара
SELECT COUNT(DISTINCT order_id)
FROM dm_items
WHERE has_canceled;

-- Самый популярный товар (за день)
SELECT item_id, SUM(item_quantity) AS qty
FROM dm_items
GROUP BY item_id
ORDER BY qty DESC
LIMIT 1;

-- Самый непопулярный
SELECT item_id, SUM(item_quantity) AS qty
FROM dm_items
GROUP BY item_id
ORDER BY qty ASC
LIMIT 1;