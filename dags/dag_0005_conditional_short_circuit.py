# -*- coding: utf-8 -*-

"""
This is an advanced example of using
`ShortCircuitOperator <https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html#shortcircuitoperator>`_. We will learn how to use custom if else logic to control the execution of downstream tasks.
"""

import random
import pendulum

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator


@dag(
    dag_id="dag_0005_conditional_short_circuit",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),  # pendulum 是一个更可靠的时区库
    schedule=None,  # 不自动执行, 你点了 Trigger DAG 才会执行
    catchup=False,
)
def my_dag():
    @task(
        task_id="task1",
    )
    def task1():
        """
        该任务 50% 几率会返回 True, 50% 几率返回 False.
        """
        print("Start task1")
        value = random.randint(1, 100)
        print(f"rnd value is {value}")
        do_we_stop_earlier = not (value > 50)
        return do_we_stop_earlier

    # short circuit operator is just a callable function
    # it can take arbitrary number of arguments from previous steps
    # you just need to return True or False
    @task.short_circuit(
        task_id="conditional_short_circuit",
    )
    def conditional_short_circuit(flag: bool):
        return flag

    run_task1 = task1()
    run_task2 = EmptyOperator(
        task_id="task2",
    )
    # conditional_short_circuit(run_task1) is the syntax to pass the returned
    # value from task1 to conditional_short_circuit
    run_task1 >> conditional_short_circuit(run_task1) >> run_task2


run_dag = my_dag()  # 你最后必须要实例化这个 DAG 对象 (它是被 @dag 装饰器装饰的函数的返回值, 不是原本的函数了)
