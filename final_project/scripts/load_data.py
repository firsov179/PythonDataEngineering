import os
import logging

import pandas as pd
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
log = logging.getLogger(__name__)

DB_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
DATA_FOLDER = "/opt/airflow/data/drive-download-20260324T150705Z-1-001"


def get_engine():
    return create_engine(DB_URL)


def read_data():
    files = [
        os.path.join(DATA_FOLDER, f)
        for f in sorted(os.listdir(DATA_FOLDER))
        if os.path.isfile(os.path.join(DATA_FOLDER, f))
    ]
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    log.info(f"Read {len(df)} rows from {len(files)} files")
    return df


def upsert(df, table, engine, conflict_cols):
    tmp = f"tmp_{table}"
    with engine.begin() as conn:
        df.to_sql(tmp, conn, if_exists='replace', index=False)
        cols = ', '.join(df.columns)
        conn.execute(text(f"""
            INSERT INTO {table} ({cols})
            SELECT {cols} FROM {tmp}
            ON CONFLICT ({conflict_cols}) DO NOTHING
        """))
        conn.execute(text(f"DROP TABLE {tmp}"))
    log.info(f"Upserted {len(df)} rows into {table}")


def load_users(df, engine):
    users = df[['user_id', 'user_phone']].drop_duplicates(subset=['user_id'])
    upsert(users, 'users', engine, 'user_id')


def load_stores(df, engine):
    stores = df[['store_id', 'store_address']].drop_duplicates(subset=['store_id'])
    upsert(stores, 'stores', engine, 'store_id')


def load_drivers(df, engine):
    drivers = df[['driver_id', 'driver_phone']].drop_duplicates(subset=['driver_id'])
    upsert(drivers, 'drivers', engine, 'driver_id')


def load_items(df, engine):
    items = df[['item_id', 'item_title', 'item_category']].drop_duplicates(subset=['item_id'])
    upsert(items, 'items', engine, 'item_id')


def load_addresses(df, engine):
    addresses = df[['address_text']].drop_duplicates(subset=['address_text']).copy()
    addresses['address_text'] = addresses['address_text'].str.strip()
    upsert(addresses, 'addresses', engine, 'address_text')



def load_orders(df, engine):
    cols = [
        'order_id', 'user_id', 'address_text', 'store_id',
        'created_at', 'paid_at', 'delivery_started_at',
        'delivered_at', 'canceled_at', 'payment_type',
        'order_discount', 'order_cancellation_reason'
    ]
    orders = df[cols].copy()

    delivered = orders.groupby('order_id')['delivered_at'].max().reset_index()
    orders = orders.drop(columns=['delivered_at']).drop_duplicates(subset=['order_id'])
    orders = orders.merge(delivered, on='order_id', how='left')

    with engine.connect() as conn:
        addr_map = pd.read_sql("SELECT address_id, address_text FROM addresses", conn)

    orders = orders.merge(addr_map, on='address_text', how='left')
    orders = orders.drop(columns=['address_text'])

    upsert(orders, 'orders', engine, 'order_id')


def load_order_drivers(df, engine):
    od = df[['order_id', 'driver_id', 'delivery_cost', 'delivered_at']].drop_duplicates(
        subset=['order_id', 'driver_id']
    ).copy()
    od['is_final'] = od['delivered_at'].notna()
    od = od.drop(columns=['delivered_at'])
    upsert(od, 'order_drivers', engine, 'order_id, driver_id')


def load_order_items(df, engine):
    cols = [
        'order_id', 'item_id', 'item_quantity', 'item_price',
        'item_canceled_quantity', 'item_replaced_id', 'item_discount'
    ]
    oi = df[cols].drop_duplicates(subset=['order_id', 'item_id']).copy()
    oi['item_replaced_id'] = oi['item_replaced_id'].astype('Int64')
    upsert(oi, 'order_items', engine, 'order_id, item_id')


def run():
    engine = get_engine()
    df = read_data()

    load_users(df, engine)
    load_stores(df, engine)
    load_drivers(df, engine)
    load_items(df, engine)
    load_addresses(df, engine)

    load_orders(df, engine)
    load_order_drivers(df, engine)
    load_order_items(df, engine)


if __name__ == "__main__":
    run()
