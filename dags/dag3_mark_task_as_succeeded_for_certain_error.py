# -*- coding: utf-8 -*-

import datetime
import pendulum

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator


class MyCustomException(Exception):
    pass


def run_task1():
    """
    该任务 100% 会抛出一个自定义异常.
    """
    print("Start task1")
    raise MyCustomException("This is a custom exception")
    print("End task1")
    return "Returned by task 1"


class MyPythonOperator(PythonOperator):
    def execute(self, context):
        try:
            return super().execute(context)
        except MyCustomException as e:
            print(f"encounter MyCustomException, which is OK")
            return "NOTHING"
        except Exception as e:
            raise e


with DAG(
    dag_id="my_dag3_mark_task_as_succeeded_for_certain_error",
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    dagrun_timeout=datetime.timedelta(seconds=10),
    catchup=False,
):
    task1 = MyPythonOperator(
        task_id="task1",
        python_callable=run_task1,
    )
    task2 = EmptyOperator(task_id="task2")
    task1 >> task2
