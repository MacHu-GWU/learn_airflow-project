# -*- coding: utf-8 -*-

import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago


HOME = Path.home()
LOG_FILE = Path(HOME, "airflow", "sanhe-test-log.txt")

def step1_callable():
    msg = "sleep for 3 sec"
    # with open(str(LOG_FILE), "a") as f:
    #     f.write(f"\n{msg}")
    print(msg)
    time.sleep(3)


def step2_callable():
    msg = "sleep for 6 sec"
    # with open(str(LOG_FILE), "a") as f:
    #     f.write(f"\n{msg}")
    print(msg)
    time.sleep(6)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

with DAG(
        "two_steps",
        description='simple two step DAG',
        start_date=days_ago(2),
        schedule_interval=timedelta(seconds=60),
        catchup=False,
) as dag:
    step1 = PythonOperator(task_id="step1", python_callable=step1_callable)
    step2 = PythonOperator(task_id="step2", python_callable=step2_callable)
    step1 >> step2
