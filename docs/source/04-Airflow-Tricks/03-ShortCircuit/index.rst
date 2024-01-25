ShortCircuit
==============================================================================


Overview
------------------------------------------------------------------------------
断路器在编排系统中是一个常见的模式. 它能让整个流程提前终止.

Airflow 有一个 `ShortCircuitOperator <https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html#shortcircuitoperator>`_ 就是干这个事情的. 它本质上是一个 task, 同时也是一个 callable, 跟普通的 Python 函数一样可以有任何参数, 只不过它必须返回 Ture 或者 False. 如果是 True 则表示我们继续执行, 当它不存在. 而如果是 False 则表示我们不执行后续的 task, 直接结束整个 DAG 的执行. 同时把所有后续的 Task 标记为 skipped, 并且整个 DAG 视为 succeeded.

我们这里有一个示例 DAG:

.. dropdown:: dag_0004_short_circuit.py

    .. literalinclude:: ../../../../dags/dag_0004_short_circuit.py
       :language: python
       :linenos:


ShortCircuit Use Case 1 - Custom Exception Handling
------------------------------------------------------------------------------
那么这个模式可以用来做什么呢? 我这里举个例子, 有的时候你有的 task 会因为各种系统原因, 例如依赖系统暂时不可用, 过一段时间你重试就好了. 所以你希望将其标记为成功, 而不希望抛出异常, 因为你认为这种情况是可以接受的. 但是这个 task 后续有很多 task, 你应该怎么做呢? 很简单. 先用 :ref:`mark-task-as-succeeded-for-certain-error` 中的方法让这个 task 返回的值中包含一个 boolean flag 用于表示是否需要执行断路器. 然后把一个 ``ShortCircuitOperator`` 放在后面, 并且接受前一个 task 的输出作为输入即可.

我们这里有一个示例 DAG:

.. dropdown:: dag_0005_conditional_short_circuit.py

    .. literalinclude:: ../../../../dags/dag_0005_conditional_short_circuit.py
       :language: python
       :linenos:
