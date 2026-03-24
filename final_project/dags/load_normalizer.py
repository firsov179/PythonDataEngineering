import sys
sys.path.insert(0, '/opt/airflow/scripts')

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from load_data import (
    read_data, get_engine,
    load_users, load_stores, load_drivers,
    load_items, load_addresses,
    load_orders, load_order_drivers, load_order_items
)

default_args = {
    'start_date': datetime(2024, 1, 1),
    'retries': 1
}


def task_load_references():
    engine = get_engine()
    df = read_data()
    load_users(df, engine)
    load_stores(df, engine)
    load_drivers(df, engine)
    load_items(df, engine)
    load_addresses(df, engine)


def task_load_orders():
    engine = get_engine()
    df = read_data()
    load_orders(df, engine)


def task_load_order_drivers():
    engine = get_engine()
    df = read_data()
    load_order_drivers(df, engine)


def task_load_order_items():
    engine = get_engine()
    df = read_data()
    load_order_items(df, engine)


with DAG(
    dag_id='dag_load_normalized',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
) as dag:

    t1 = PythonOperator(
        task_id='load_references',
        python_callable=task_load_references
    )

    t2 = PythonOperator(
        task_id='load_orders',
        python_callable=task_load_orders
    )

    t3 = PythonOperator(
        task_id='load_order_drivers',
        python_callable=task_load_order_drivers
    )

    t4 = PythonOperator(
        task_id='load_order_items',
        python_callable=task_load_order_items
    )

    t1 >> t2 >> [t3, t4]
