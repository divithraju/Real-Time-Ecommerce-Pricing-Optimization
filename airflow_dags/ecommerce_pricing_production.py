from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from ingestion.fetch_products import main as fetch_products_main

default_args = {
    'owner': 'divithraju',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['divithraju@gmail.com'],
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

with DAG('ecommerce_pricing_production',
         default_args=default_args,
         description='Daily production-grade pricing pipeline with model training & scoring',
         schedule_interval='0 3 * * *',
         start_date=datetime(2024,2,1),
         catchup=False) as dag:

    t1_ingest = PythonOperator(
        task_id='ingest_products',
        python_callable=fetch_products_main
    )

    t2_sqoop = BashOperator(
        task_id='sqoop_import_historical',
        bash_command='bash sqoop_ingestion/sqoop_import_product_sales.sh || true'
    )

    t3_etl = BashOperator(
        task_id='spark_etl',
        bash_command='spark-submit --master local[*] spark_transform/sales_transform_job.py'
    )

    t4_train = BashOperator(
        task_id='train_model',
        bash_command='spark-submit --master local[*] spark_ml/train_pricing_model.py'
    )

    t5_score = BashOperator(
        task_id='batch_score',
        bash_command='spark-submit --master local[*] spark_ml/batch_score.py || true'
    )

    t6_validate = BashOperator(
        task_id='validate',
        bash_command='python3 validation/data_quality_check.py || true'
    )

    t1_ingest >> t2_sqoop >> t3_etl >> t4_train >> t5_score >> t6_validate
