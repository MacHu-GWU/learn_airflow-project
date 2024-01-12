Airflow Overview
==============================================================================


What is Airflow
------------------------------------------------------------------------------
Airflow 是由 Airbnb 公司开发, 后来捐献给 Apache 软件基金会的开源项目. 它是个 Workflow Orchestration (工作流编排) 的 Service (服务) 端软件.

为了更好的理解 Airflow 具体解决了什么问题, 我们先来理解下 **什么是 Workflow Orchestration (工作流编排)**.

Workflow (也叫 工作流) 是一个由多个 Task (也叫 任务) 按照顺序和依赖关系组成的.

举个例子, 你有几个 Task 要做. 每个 Task 可能是执行一段代码, 远程执行服务器上的程序 或是任何事情. 这些 Task 之间有互相依赖的关系. 有的 Task 需要其他 Task 成功完成后才能开始. 有的 Task 成功或是失败后执行不同的 Task. 有的 Task 需要并行或者串行执行. Task 之间还可能互相传递数据和参数. 失败后有的需要重试. 这, 就叫做 Workflow Orchestration.

那么, 我们 **为什么需要用 Airflow 来做 Workflow Orchestration 呢**?

首先, 每运行第一个 task 就会涉及到运行的计算环境, 可能是虚拟机, 可能是容器, 可能是数据库. 而这个运行的逻辑一般是用代码来实现的. 环境可能因为各种原因例如网络变得不可用, 而代码更是可能出错导致无法运行.

其次, 那么当 Workflow 中的 Task 很多, 之间的关系又非常复杂时, 能稳定的按照逻辑执行下来并记录日志和状态就不是很容易了.

这就使得一个外部管理者的角色来进行调度, 并检测每个 task 的运行状态, 并且提供一个可视化界面来查看 task 的运行状态和日志就成为了刚需. 而这个外部管理者就是 Airflow.

而 Airflow 是一个 Python 写的服务器, 允许你以单点或是集群, 虚拟机或是容器的方式部署. 同时 Airflow 也是一个 Python 库, 允许你用 Python 方便滴定义你的 Workflow 以及 Task, 然后 Submit 到 服务器上定时运行. 并且这个服务器还自带 UI 界面, 可以方便的查看你的 Workflow 的状态以及日志. 当然命令行工具以及 Python 运行也都是允许的.

因为我是 AWS 的重度开发者, 这里有必要提一嘴 AWS Step Function, 一个无服务器的编排服务. 本质上 Airflow 的很多功能和 AWS Step Function 是重合的, 不过 Airflow 更加通用, 且更加被业内所广泛使用.


Airflow 的 核心组件 和 概念
------------------------------------------------------------------------------
- Web Server: 一个 Web UI 的服务器组件.
- Scheduler: Airflow 调度器, 决定了什么时候, 分配哪个 Executor 来执行哪个 Workflow. 内部 Airflow 有一个 Message Queue 来管理事件的触发, 比如触发执行任务.
- Executor: Airflow 执行器, Workflow 和 Task 会被交给 Executor 来执行, 本质上是一个进程.
- Database: Airflow 需要连接到一台 SQL Database 来保存状态数据, 在集群部署时也是中心化的状态数据存储. 并且用于 task 之间通信的 XCom (cross communication) 也是通过将输入输出数据序列化存到数据库中实现的.
- DAG: 有向无环图. Workflow 在程序上的抽象就是一个 DAG. 你只要定义了每个 Node 和 Edge, 那么你的 Workflow 的逻辑也就出来了. 每个 Node 有很多 Attribute, 比如 Id, Argument. 每个 Workflow 最终就是一个 ``.py`` 文件, 里面必须要有一个 DAG 的实例.
- Operator: Operator 就是在 python code 里的实现, 是一个类. 每个 Task 本质上就是一个 Callable 的函数, 可以抛出异常, 可以休眠, 可以重试.


Airflow 服务器的部署
------------------------------------------------------------------------------
Airflow 本身是一个服务器. 对于生产环境, 肯定是需要以集群的方式运作才能保证不丢数据以及高可用. 换言之, 你需要配置一个集群, 然后都安装 Airflow 软件, 以及用配置文件定义谁是 Web Server, 谁是 Scheduler, 谁是 Executor.

听起来就不简单对吗? 没错, 这也是市场上有很多 Airflow 即服务的产品以及 Vendor 存在的原因. 通常这些 Vendor 会允许你用一个简单的界面点几下鼠标, 就能自动创建一个 Airflow 集群, 而集群的健康, 数据库, 网络都是由 Vendor 管理, 你只需要交钱就行了. 这里面的主要提供商有:

- `astronomer.io <https://www.astronomer.io/>`_:
- `Amazon MWAA <https://aws.amazon.com/managed-workflows-for-apache-airflow/>`_:


Amazon MWAA
------------------------------------------------------------------------------
由于我是重度 AWS 用户, 所以有必要单独开一小节来简单介绍下 MWAA.

它的全称是 AWS Managed Workflows for Apache Airflow. 我们简称 AWS Airflow. 是 AWS 的一个 Airflow 托管服务. 允许你一键部署 Airflow 集群, 并且自带数据库和UI. 从 AWS S3 读取 dag 文件, 以及依赖包, 还有 requirements.txt 文件. 并且和 AWS 自带的

出于安全考虑, AWS Airflow 只能部署部署在 Private Subnet 上. 并且 AWS 会自动帮你配置好 Web UI 的 Endpoint, 基于 IAM Role 控制访问 Web UI 的权限. 并且用 IAM Role 来管理 Airflow 对 AWS 资源的访问权限.


Airflow Alternative
------------------------------------------------------------------------------
- `airflow <https://airbyte.com/>`_: data pipeline 界的 airflow
- `dagster <https://dagster.io/>`_: 另一个 data pipeline 界的 airflow
- `y42 <https://www.y42.com/>`_: 另一个 data pipeline 界的 airflow


How to Learn Airflow
------------------------------------------------------------------------------
最好的学习方法一定是动手实践. 但 Airflow 是一个服务器软件. 你需要搭建好 Airflow 集群服务器才能在上面跑程序. 但在实际工作中, 大部分人都是负责 Airflow 程序的开发, 而只有少部分人需要负责管理和运维 Airflow 集群. 对于开发者而言, 为了自己学习, 也必须要懂一点管理和运维知识, 这对于很多人来说是一个挑战.

我推荐以下两种方法:

1. 在本地安装 Airflow 并启动 UI 和 Scheduler. 这是一个单点部署的服务器. 在这上面你可以专注于学习如何写 Airflow 程序. 具体步骤可以参考 :ref:`setup-airflow-locally-for-development`.
2. 使用第三方托管的 Airflow 平台, 并且按需付费, 学习完之后关闭集群即可. 我个人比较喜欢的几个平台:
    - `astronomer.io <https://www.astronomer.io/>`_: 一个专门提供 Airflow 托管服务的公司. 他们提供了免费的试用期, 最小配置的价格是 $0.35 / Hour.
    - `AWS MWAA <https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html>`_: AWS 提供的全托管 Airflow. 比较贵, 但更接近于生产环境的实际情况. 最小配置的价格是 $0.59 / Hour. 我个人比较推荐.

我个人比较推荐先拿 1 上手, 专注于学习到如何写 dag, 如何测试, 如何实现常见的调度模型, 例如串行, 并行, 条件判断等. 接下来就可以用 AWS MWAA 配置跟生产环境类似的服务器集群, 当然你不用的时候就可以关掉, 不用付费.


Reference
------------------------------------------------------------------------------
- `Airflow Doc <https://airflow.apache.org/docs/apache-airflow/stable/index.html>`_
- `AWS MWAA Doc <https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html>`_
- `Airflow Architect Overview <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html>`_
