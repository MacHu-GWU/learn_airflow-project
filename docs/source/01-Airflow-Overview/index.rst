Airflow Overview
==============================================================================


How to Learn Airflow
------------------------------------------------------------------------------
最好的学习方法一定是动手实践. 但 Airflow 是一个服务器软件. 你需要搭建好 Airflow 集群服务器才能在上面跑程序. 但在实际工作中, 大部分人都是负责 Airflow 程序的开发, 而只有少部分人需要负责管理和运维 Airflow 集群. 对于开发者而言, 为了自己学习, 也必须要懂一点管理和运维知识, 这对于很多人来说是一个挑战.

我推荐以下两种方法:

1. 在本地安装 Airflow 并启动 UI 和 Scheduler. 这是一个单点部署的服务器. 在这上面你可以专注于学习如何写 Airflow 程序.
2. 使用第三方托管的 Airflow 平台, 并且按需付费, 学习完之后关闭集群即可. 我个人比较喜欢的几个平台:
    - `AWS MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html>`_: AWS 提供的全托管 Airflow. 比较贵, 但更接近于生产环境的实际情况. 最小配置的价格是 $0.59 / Hour. 推荐.
    - `astronomer.io <https://www.astronomer.io/>`_: 一个专门提供 Airflow 托管服务的公司. 他们提供了免费的试用期, 最小配置的价格是 $0.35 / Hour.


Architecture Overview
------------------------------------------------------------------------------
Airflow 一共有三个组件:

1. Web UI. 它是一个基于 Flask 的 Web App, 能看到所有的 DAG, Task, Task Instance 的状态, 也能手动触发 DAG 的运行. 用户可以通过 DAG 来 debug.
2. Scheduler. 调度器, 它是一个 Airflow 程序, 本质上是用来调度如何执行 DAG 的. DAG 程序本身不在这上面跑.
3. Executor. 执行器, 它是一个 Airflow 的异步程序, 可以在上面执行具体的 DAG 任务. 本质上是对你的 Python 程序的二次封装.

在生产环境中, 以上三个部分一般会分开部署, 并且每个部分都有多个节点来保持高可用以及随时能横向扩展.

Reference:

- `Airflow Architect Overview <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html>`_
