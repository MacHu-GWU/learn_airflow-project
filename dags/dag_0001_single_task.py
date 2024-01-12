# -*- coding: utf-8 -*-

"""
简单的单步任务.
"""

import pendulum

from airflow.decorators import dag, task


@dag(
    dag_id="dag_0001_single_task",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"), # pendulum 是一个更可靠的时区库
    schedule=None,  # 不自动执行, 你点了 Trigger DAG 才会执行
    catchup=False,
)
def my_dag():
    """
    这个例子中只有一个 Task.
    """
    task1_id = "task1"

    @task(
        task_id=task1_id,
    )
    def task1():
        """
        该任务随机生成一个 1 - 100 的随机数, 并将这个值和当前的事件一起写入到 S3 中.
        """
        # 注意, 任何跟执行任务相关, 需要 import 的包, 都需要在函数内部 import.
        # 因为 task 函数外部的内容都属于调度器的运行环境, 而 task 函数内则是执行器的运行环境
        # 通常情况下, 调度器只要有 Airflow 服务器自带的包就够了, 而执行器很可能需要在
        # virtualenv 中运行, 可能需要任何包.
        # Ref: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#top-level-python-code
        import random

        print("Start task1")

        value = random.randint(1, 100)
        print(f"Generated value is {value}")

        print("End task1")
        # 在 Python Operator (也就是 @task 装饰器装饰的函数) 中, 返回值将会被视为 Task Output
        # 这个返回值一定要是一个可序列化的对象, 因为 Airflow 会自动负责将这个对象序列化后以备
        # 后续的 task 使用 (虽然这个例子中没有).
        return "Returned by task 1"

    run_task1 = task1()  # 你只要调用这个 task 函数就相当于告诉 Airflow 我要运行这个 task 了.


run_dag = my_dag()  # 你最后必须要实例化这个 DAG 对象 (它是被 @dag 装饰器装饰的函数的返回值, 不是原本的函数了)
