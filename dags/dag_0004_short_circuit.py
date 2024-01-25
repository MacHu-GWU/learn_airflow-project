# -*- coding: utf-8 -*-

"""
This example shows how to use
`ShortCircuitOperator <https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html#shortcircuitoperator>`_
to skip downstream tasks.
"""

import pendulum

from airflow.decorators import dag
# you need to import ShortCircuitOperator
from airflow.operators.python import ShortCircuitOperator
from airflow.operators.empty import EmptyOperator


@dag(
    dag_id="dag_0004_short_circuit",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),  # pendulum 是一个更可靠的时区库
    schedule=None,  # 不自动执行, 你点了 Trigger DAG 才会执行
    catchup=False,
)
def my_dag():
    task1 = EmptyOperator(
        task_id="task1",
    )
    # short circuit operator is just a callable function, however,
    # it has to return a boolean value, True or False.
    # If True, then keep going,
    # If False, then skip all downstream tasks.
    cond = ShortCircuitOperator(
        task_id="condition",
        python_callable=lambda: False,
    )
    task2 = EmptyOperator(
        task_id="task2",
    )
    task1 >> cond >> task2


run_dag = my_dag()  # 你最后必须要实例化这个 DAG 对象 (它是被 @dag 装饰器装饰的函数的返回值, 不是原本的函数了)
