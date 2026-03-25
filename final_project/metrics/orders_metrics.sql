-- Оборот
SELECT SUM(turnover) FROM dm_orders;

-- Выручка
SELECT SUM(revenue) FROM dm_orders;

-- Прибыль
SELECT SUM(profit) FROM dm_orders;

-- Заказы
SELECT COUNT(*) FROM dm_orders;

-- Доставленные
SELECT COUNT(*) FROM dm_orders WHERE is_delivered;

-- Отмененные
SELECT COUNT(*) FROM dm_orders WHERE is_canceled;

-- Отмены после доставки
SELECT COUNT(*) FROM dm_orders WHERE cancel_after_delivery;

-- Ошибки сервиса
SELECT COUNT(*) FROM dm_orders WHERE cancel_service_fault;

-- Покупатели
SELECT COUNT(DISTINCT user_id) FROM dm_orders;

-- Средний чек
SELECT AVG(revenue) FROM dm_orders;

-- Заказов на пользователя
SELECT COUNT(*) * 1.0 / COUNT(DISTINCT user_id) FROM dm_orders;

-- Выручка на пользователя
SELECT SUM(revenue) * 1.0 / COUNT(DISTINCT user_id) FROM dm_orders;

-- Заказы со сменой курьера
SELECT COUNT(*) FROM dm_orders WHERE has_driver_change;

-- Активные курьеры
SELECT COUNT(DISTINCT final_driver_id)
FROM dm_orders
WHERE is_delivered;