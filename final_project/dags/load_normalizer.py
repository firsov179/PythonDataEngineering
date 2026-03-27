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

from build_marts_sql import (
    build_order_mart, build_item_mart
)

default_args = {
    'start_date': datetime(2024, 1, 1),
    'retries': 1
}

def task_read_data(**kwargs):
    df = read_data()
    kwargs['ti'].xcom_push(key='dataframe', value=df)
    return df

def task_load_references(**kwargs):
    engine = get_engine()
    df = kwargs['ti'].xcom_pull(key='dataframe', task_ids='read_data')
    load_users(df, engine)
    load_stores(df, engine)
    load_drivers(df, engine)
    load_items(df, engine)
    load_addresses(df, engine)


def task_load_orders(**kwargs):
    engine = get_engine()
    df = kwargs['ti'].xcom_pull(key='dataframe', task_ids='read_data')
    load_orders(df, engine)


def task_load_order_drivers(**kwargs):
    engine = get_engine()
    df = kwargs['ti'].xcom_pull(key='dataframe', task_ids='read_data')
    load_order_drivers(df, engine)


def task_load_order_items(**kwargs):
    engine = get_engine()
    df = kwargs['ti'].xcom_pull(key='dataframe', task_ids='read_data')
    load_order_items(df, engine)

def task_build_order_mart():
    build_order_mart()

def task_build_item_mart():
    build_item_mart()


with DAG(
    dag_id='dag_load_normalized',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
) as dag:

    read_data_task = PythonOperator(
        task_id='read_data',
        python_callable=task_read_data
    )

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

    t5 = PythonOperator(
        task_id='build_order_mart',
        python_callable=task_build_order_mart
    )

    t6 = PythonOperator(
        task_id='build_item_mart',
        python_callable=task_build_item_mart
    )

    read_data_task >> t1 >> t2 >> t3 >> t4 >> t5 >> t6
