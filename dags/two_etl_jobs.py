# -*- coding: utf-8 -*-

import time
import random
import pynamodb

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

from pathlib import Path
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

HOME = Path.home()
LOG_FILE = Path(HOME, "airflow", "sanhe-test-log.txt")


class ETLJob(Model):
    class Meta:
        table_name = "airflow_poc_etl_job"
        region = "us-east-1"
        billing_mode = pynamodb.models.PAY_PER_REQUEST_BILLING_MODE

    job_id = UnicodeAttribute(hash_key=True)
    status = UnicodeAttribute()
    start_time = UnicodeAttribute()
    end_time = UnicodeAttribute(null=True)


ETLJob.create_table(wait=True)


class Status:
    running = "running"
    success = "success"
    failed = "failed"


def etl_job_1(job_id):
    """
    ETL job 1:

    - takes 10 seconds to complete
    - 70% chance success, 30% failed
    """
    job = ETLJob(
        job_id=job_id,
        status=Status.running,
        start_time=str(datetime.utcnow()),
        end_time=None
    )
    job.save()

    print("run etl job 1, need 10 seconds")
    time.sleep(5)
    if random.randint(1, 100) <= 30:
        job.status = Status.failed
        job.end_time = str(datetime.utcnow())
        job.save()
        print("failed")
        raise Exception

    time.sleep(5)
    job.status = Status.success
    job.end_time = str(datetime.utcnow())
    job.save()
    print("success")


def etl_job_2(job_id):
    """
    ETL job 2:

    - takes 20 seconds to complete
    - 70% chance success, 30% failed
    """
    job = ETLJob(
        job_id=job_id,
        status=Status.running,
        start_time=str(datetime.utcnow()),
        end_time=None
    )
    job.save()

    print("run etl job 2, need 20 seconds")
    time.sleep(10)
    if random.randint(1, 100) <= 30:
        job.status = Status.failed
        job.end_time = str(datetime.utcnow())
        job.save()
        print("failed")
        raise Exception

    time.sleep(10)
    job.status = Status.success
    job.end_time = str(datetime.utcnow())
    job.save()
    print("success")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
        "two_etl_jobs",
        description='simple two step DAG',
        start_date=days_ago(2),
        schedule_interval=timedelta(seconds=60),
        catchup=False,
) as dag:
    step1 = PythonOperator(
        task_id="step1",
        python_callable=etl_job_1,
        op_kwargs=dict(job_id="job_1"),
    )
    step2 = PythonOperator(
        task_id="step2",
        python_callable=etl_job_2,
        op_kwargs=dict(job_id="job_2"),
    )
    step1 >> step2
