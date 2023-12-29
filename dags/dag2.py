# -*- coding: utf-8 -*-

"""
在任务之间传递参数.
"""

from datetime import datetime
from airflow.decorators import dag, task

dag_id = "dag2"


@dag(
    dag_id=dag_id,
    start_date=datetime(2021, 1, 1),
    schedule="@once",
    catchup=False,
)
def dag2():
    """
    这个例子中只有一个 Task.
    """
    @task(
        task_id="task1",
    )
    def task1():
        return 1, 2

    @task(
        task_id="task2",
    )
    def task2(a, b):
        print("total is", a + b)

    run_task1 = task1()  # 你只要调用这个 task 函数就相当于告诉 Airflow 我要运行这个 task 了.
    run_task1 >> task2(run_task1[0], run_task1[1])


run_dag2 = dag2()
