Callback
==============================================================================


Overview
------------------------------------------------------------------------------

`Callback <https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/callbacks.html>`_ 是 Airflow 的一个机制, 可以在某些事件发生时调用一个 Python 函数. 例如在 task 失败的时候发 email 提醒等. Airflow 支持下列 callback:

- ``on_success_callback``: Invoked when the task succeeds
- ``on_failure_callback``: Invoked when the task fails
- ``sla_miss_callback``: Invoked when a task misses its defined SLA (Service Level Agreements)
- ``on_retry_callback``: Invoked when the task is up for retry
- ``on_execute_callback``: Invoked right before the task begins executing.

这些参数是要在你用 ``@task`` decorator 或是 ``BaseOperator`` 的时候传入的 (所有的 Operator 都支持这些参数). 不然是不会有作用的.

这里有一个小坑. 如果你用了 ``@dag`` + ``@task`` 定义了你的 dag 和 task, 按照官方文档, 如果你在 dag 级别定义了任何 callback, 所有的 task 是可以自动获得这些 callback 的. 但是官方文档没有说, 你不许用 ``with DAG(...)`` 以及 ``PythonOperator(...)`` 这样的形式定义才能有这个效果. 而用 decorator 是没有这个效果的, 你需要给每个 task 一个个的定义.

下面我们给出了一个示例 dag:

.. literalinclude:: ../../../../dags/dag_0002_callback.py
   :language: python
   :linenos:
