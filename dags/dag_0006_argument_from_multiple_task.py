# -*- coding: utf-8 -*-

import pendulum

from airflow.decorators import dag, task


@dag(
    dag_id="dag_0006_argument_from_multiple_task.py",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),  # pendulum 是一个更可靠的时区库
    schedule=None,  # 不自动执行, 你点了 Trigger DAG 才会执行
    catchup=False,
)
def my_dag():
    @task(
        task_id="task1",
    )
    def task1():
        return "This is task 1"

    @task(
        task_id="task2",
    )
    def task2():
        return "This is task 1"

    @task(
        task_id="task3",
    )
    def task3(text1: str, text2: str):
        print(f"{text1 = }, {text2 = }")

    run_task1 = task1()
    run_task2 = task2()
    run_task1 >> run_task2 >> task3(run_task1, run_task2)


run_dag = my_dag()  # 你最后必须要实例化这个 DAG 对象 (它是被 @dag 装饰器装饰的函数的返回值, 不是原本的函数了)
