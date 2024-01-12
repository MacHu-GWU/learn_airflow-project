Airflow Knowledge Graph
==============================================================================
本文档把所有 Airflow 的知识点汇总在一起, 不对知识内容做详细解释, 只是梳理一遍知识点和这些知识点的作用, 以及列出相关文档. 以便查阅.


调度相关
------------------------------------------------------------------------------
- **简单的单步任务**:
- **简单的两步任务, 串行**:
    - `Task Relationship <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html#relationships>`_
- **简单的两步任务, 并行**:
    - `Task Relationship <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html#relationships>`_
- **使用第三方 Python 包**: 如果你有很多任务会需要不同的第三方包, 你很难找到一个通用的依赖配置, 如何让不同的 task 有不同的依赖层?
- **在相邻的两个 Task 之间传递数据**:
- **在任意的两个 Task 之间传递小数据**: 任意的意思是它们可能不相邻
    - `用于传递数据的 XComs 概念介绍 <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html>`_
- **在任意的两个 Task 之间传递大数据**: 任意的意思是它们可能不相邻
- **Poll for Job Status 模式**: 远程异步调用位于 Airflow 之外的任务, 并查询任务状态, 直到任务完成或失败
    - `Core Concepts - Sensors <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/sensors.html>`_: 解决这一问题的核心概念 sensor 的介绍.
    - `Using the TaskFlow API with Sensor operators <https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html#using-the-taskflow-api-with-sensor-operators>`_: 官方使用 sensor 的 示例代码
- **Failure tolerance in parallel tasks**: 在多个并行任务的下一步都指向同一个任务时, 这一批并行任务到底允不允许部分失败? 能允许多少?
    - `Trigger Rules <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#trigger-rules>`_: 定义失败容忍规则的官方文档.
- **单个任务失败重试**: 任务失败后, 重试多少次? 重试间隔是多少? 要不要以 exponential backoff 的方式等待? 相关文档:
    - https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#trigger-rules
- **Timeout**: 对单个 task 或者整个 dag 设定 timeout
    - `Task Timeout <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html#timeouts>`_: 请看 ``execution_timeout`` 这一参数.
    - `Dag Timeout <https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/dag/index.html#airflow.models.dag.DAG>`_: 请看 ``dagrun_timeout`` 这一参数.
- **条件分叉执行**: 一个任务之后接着多条链路, 根据这个任务的结果判断我们选择哪条链路执行. 相关文档:
    - `Branching <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#branching>`_: 介绍 branching 概念的官方文档
    - `BranchPythonOperator <https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/python/index.html#airflow.operators.python.BranchPythonOperator>`_: 实现 branching 的 operator 的 API 文档
- **断路器**: 一个任务执行完之后, 根据结果选择是否要提前结束整个链路.
    -`Short circuit Operator <https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html#howto-operator-shortcircuitoperator>`_: 对断路器模式的介绍.
    - `ShortCircuitOperator <https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/python/index.html#airflow.operators.python.ShortCircuitOperator>`_: 实现断路器的 operator 的 API 文档.


开发技巧相关
------------------------------------------------------------------------------
- 老式的 context manager + operator 的写法:
- 新式的 task flow decorator 的写法:
    - `Task flow 介绍 <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/taskflow.html>`_
- 用 UI 运行的 Dag 时使用 fancy 的表单界面来决定输入的 parameters:
    - `Params 介绍 <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/params.html>`_
- 给你的 Airflow 环境添加 Variables 并在 task 中访问这些 Variables:
    - `Variables 介绍 <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/variables.html>`_
- 在多个 Task 之间分享 dataset 数据, 从而避免每个 task 都要 IO:
    - `Dataset 介绍 <https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/datasets.html#what-is-a-%22dataset%22?>`_
- 用 Code 来生成 Dag 以及里面的逻辑而不是手写函数定义 dag:
    - `关键技术 dynamic dag 介绍 <https://airflow.apache.org/docs/apache-airflow/stable/howto/dynamic-dag-generation.html>`_
- 动态的创建多个 Task: 常用语根据输入的参数, 启用 N 个 (N 是变量) parallel task 的情况.
    - `Dynamic Task Mapping <https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html>`_


安全相关
------------------------------------------------------------------------------
- **如何在 Airflow 中保存敏感数据, 例如数据库连接信息**:
