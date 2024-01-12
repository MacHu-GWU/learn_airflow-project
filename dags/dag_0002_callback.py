# -*- coding: utf-8 -*-

"""
学习如何使用 callback 函数在 任务成功, 失败, 重试的时候执行一些操作.

Reference:

- https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/callbacks.html
"""

import pendulum

from airflow.decorators import dag, task

# 由于 decorator 的参数由于其实现原理比较 tricky, IDE 不能自动提示,
# 但我们知道它的参数跟 Operator class 的参数一致, 所以我这里 import 进来供我点击跳转查看参数.
from airflow.operators.python import BaseOperator


def on_success_callback(context):
    print("I called on_success_callback")


def on_failure_callback(context):
    print("I called on_failure_callback")


def on_retry_callback(context):
    print("I called on_retry_callback")


@dag(
    dag_id="dag_0002_callback",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),  # pendulum 是一个更可靠的时区库
    schedule=None,  # 不自动执行, 你点了 Trigger DAG 才会执行
    catchup=False,
)
def my_dag():
    @task(
        task_id="task1",
        on_success_callback=on_success_callback,
    )
    def task1():
        """
        Task 1 永远成功.
        """
        print("Start task1")
        print("End task1")

    @task(
        task_id="task2",
        retries=10,
        retry_delay=1,
        on_retry_callback=on_retry_callback,
    )
    def task2():
        """
        Task 2 只有 10% 的概率成功. 但是我们重试 10 次, 按概率 10 次全部失败的概率是 35%, 并不低.
        """
        import random

        print(f"Start task2")
        value = random.randint(1, 100)
        print(f"Generated value is {value}")
        if value <= 10:
            pass
        else:
            raise ValueError("Randomly failed")

        print("End task2")

    @task(
        task_id="task3",
        on_failure_callback=on_failure_callback,
    )
    def task3():
        """
        Task 3 永远失败.
        """
        print("Start task3")
        raise Exception("Always failed")
        print("End task3")

    run_task1 = task1()
    run_task2 = task2()
    run_task3 = task3()

    run_task1 >> run_task2 >> run_task3


run_dag = my_dag()  # 你最后必须要实例化这个 DAG 对象 (它是被 @dag 装饰器装饰的函数的返回值, 不是原本的函数了)
