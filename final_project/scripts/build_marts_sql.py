import logging
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
log = logging.getLogger(__name__)

DB_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

def get_engine():
    return create_engine(DB_URL)

def build_order_mart():
    engine = get_engine()
    
    log.info("Building order mart...")
    
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE dm_orders"))
        
        conn.execute(text("""
            INSERT INTO dm_orders (
                order_id, user_id, store_id, address_text,
                order_date, year, month, day,
                turnover, revenue, profit,
                is_delivered, is_canceled, cancel_after_delivery,
                cancel_service_fault, has_driver_change, final_driver_id
            )
            WITH 
            order_finance AS (
                SELECT 
                    oi.order_id,
                    SUM((oi.item_price * oi.item_quantity) - COALESCE(oi.item_discount, 0)) AS turnover,
                    SUM(
                        (oi.item_quantity - COALESCE(oi.item_canceled_quantity, 0)) * oi.item_price 
                        - COALESCE(oi.item_discount, 0)
                    ) AS revenue,
                    COALESCE(o.order_discount, 0) AS order_discount
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                GROUP BY oi.order_id, o.order_discount
            ),
            driver_stats AS (
                SELECT 
                    order_id,
                    COUNT(*) AS driver_count,
                    SUM(delivery_cost) AS total_delivery_cost,
                    MAX(CASE WHEN is_final THEN driver_id END) AS final_driver_id
                FROM order_drivers
                GROUP BY order_id
            )
            SELECT 
                o.order_id,
                o.user_id,
                o.store_id,
                a.address_text,
                DATE(o.created_at) AS order_date,
                EXTRACT(YEAR FROM o.created_at) AS year,
                EXTRACT(MONTH FROM o.created_at) AS month,
                EXTRACT(DAY FROM o.created_at) AS day,
                f.turnover - COALESCE(f.order_discount, 0) AS turnover,
                f.revenue - COALESCE(f.order_discount, 0) AS revenue,
                (f.revenue - COALESCE(f.order_discount, 0)) - COALESCE(d.total_delivery_cost, 0) AS profit,
                o.delivered_at IS NOT NULL AS is_delivered,
                o.canceled_at IS NOT NULL AS is_canceled,
                (o.canceled_at IS NOT NULL AND o.delivered_at IS NOT NULL) AS cancel_after_delivery,
                o.order_cancellation_reason IN ('Ошибка приложения', 'Проблемы с оплатой') AS cancel_service_fault,
                COALESCE(d.driver_count, 0) > 1 AS has_driver_change,
                d.final_driver_id
            FROM orders o
            LEFT JOIN order_finance f ON o.order_id = f.order_id
            LEFT JOIN driver_stats d ON o.order_id = d.order_id
            LEFT JOIN addresses a ON o.address_id = a.address_id
        """))
        
        result = conn.execute(text("SELECT COUNT(*) FROM dm_orders")).scalar()
        log.info(f"Loaded {result} rows into dm_orders")
    
    return result

def build_item_mart():
    engine = get_engine()
    
    log.info("Building item mart...")
    
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE dm_items"))
        
        conn.execute(text("""
            INSERT INTO dm_items (
                order_id, user_id, store_id, item_id, item_title, item_category,
                order_date, year, month, day,
                item_quantity, item_canceled_quantity, item_turnover, has_canceled
            )
            SELECT 
                oi.order_id,
                o.user_id,
                o.store_id,
                oi.item_id,
                i.item_title,
                i.item_category,
                DATE(o.created_at) AS order_date,
                EXTRACT(YEAR FROM o.created_at) AS year,
                EXTRACT(MONTH FROM o.created_at) AS month,
                EXTRACT(DAY FROM o.created_at) AS day,
                oi.item_quantity,
                COALESCE(oi.item_canceled_quantity, 0) AS item_canceled_quantity,
                (oi.item_price * oi.item_quantity) - COALESCE(oi.item_discount, 0) AS item_turnover,
                COALESCE(oi.item_canceled_quantity, 0) > 0 AS has_canceled
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN items i ON oi.item_id = i.item_id
        """))
        
        result = conn.execute(text("SELECT COUNT(*) FROM dm_items")).scalar()
        log.info(f"Loaded {result} rows into dm_items")
    
    return result
