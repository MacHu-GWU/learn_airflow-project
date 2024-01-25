# -*- coding: utf-8 -*-

import pendulum

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator


class MyCustomException(Exception):
    pass


class MyPythonOperator(PythonOperator):
    def execute(self, context):
        try:
            return super().execute(context)
        except MyCustomException as e:
            print(f"encounter MyCustomException, which is OK")
            return "NOTHING"
        except Exception as e:
            raise e


def run_task1():
    """
    该任务 100% 会抛出一个自定义异常.
    """
    print("Start task1")
    raise MyCustomException("This is a custom exception")
    print("End task1")
    return "Returned by task 1"


@dag(
    dag_id="dag_0003_mark_task_as_succeeded_for_certain_error",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),  # pendulum 是一个更可靠的时区库
    schedule=None,  # 不自动执行, 你点了 Trigger DAG 才会执行
    catchup=False,
)
def my_dag():
    task1 = MyPythonOperator(
        task_id="task1",
        python_callable=run_task1,
    )
    task2 = EmptyOperator(task_id="task2")
    task1 >> task2


run_dag = my_dag()  # 你最后必须要实例化这个 DAG 对象 (它是被 @dag 装饰器装饰的函数的返回值, 不是原本的函数了)
