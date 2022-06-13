import os


from datetime import datetime, timezone


from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from etl_first_run import run_etl

args = {"owner": "Airflow", "start_date": days_ago(1)}

dag = DAG(dag_id="etl_second_dag", default_args=args, schedule_interval='0 16 * * *')

with dag:
    import logging

    today = datetime.now()
    log_time = today.strftime("%a_%b_%d_%Y_%X")
    log_file = f'etl_second_run{log_time}.log'
    logging.basicConfig(filename=log_file,filemode='w', format='[%(levelname)s]: %(message)s', level=logging.DEBUG)
    
    etl_second_task = PythonOperator(task_id="etl_second_task", python_callable=run_etl)

    etl_second_task
