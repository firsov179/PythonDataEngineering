CREATE TABLE IF NOT EXISTS users (
    user_id                    BIGINT PRIMARY KEY,
    user_phone                 VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS stores (
    store_id                   BIGINT PRIMARY KEY,
    store_address              TEXT
);

CREATE TABLE IF NOT EXISTS drivers (
    driver_id                  BIGINT PRIMARY KEY,
    driver_phone               VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS items (
    item_id                    BIGINT PRIMARY KEY,
    item_title                 TEXT,
    item_category              TEXT
);

CREATE TABLE IF NOT EXISTS addresses (
    address_id                 SERIAL PRIMARY KEY,
    address_text               TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id                   BIGINT PRIMARY KEY,
    user_id                    BIGINT REFERENCES users(user_id),
    address_id                 INTEGER REFERENCES addresses(address_id),
    store_id                   BIGINT REFERENCES stores(store_id),
    created_at                 TIMESTAMP,
    paid_at                    TIMESTAMP,
    delivery_started_at        TIMESTAMP,
    delivered_at               TIMESTAMP,
    canceled_at                TIMESTAMP,
    payment_type               VARCHAR(50),
    order_discount             INTEGER,
    order_cancellation_reason  TEXT
);

CREATE TABLE IF NOT EXISTS order_drivers (
    id                         SERIAL PRIMARY KEY,
    order_id                   BIGINT REFERENCES orders(order_id),
    driver_id                  BIGINT REFERENCES drivers(driver_id),
    delivery_cost              INTEGER,
    is_final                   BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (order_id, driver_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id                         SERIAL PRIMARY KEY,
    order_id                   BIGINT REFERENCES orders(order_id),
    item_id                    BIGINT REFERENCES items(item_id),
    item_quantity              INTEGER,
    item_price                 INTEGER,
    item_canceled_quantity     INTEGER,
    item_replaced_id           BIGINT REFERENCES items(item_id),
    item_discount              INTEGER,
    UNIQUE (order_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_store_id ON orders(store_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_drivers_order_id ON order_drivers(order_id);
