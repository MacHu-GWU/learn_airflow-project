.. _setup-airflow-locally-for-development:

Setup Airflow Locally For Development
==============================================================================


Objectives
------------------------------------------------------------------------------
本节我们的目的是在本地配置好一个 Airflow 的开发环境. 使得我们能写 dag code, 并在 Airflow 中测试运行.


Install Airflow
------------------------------------------------------------------------------
首先我们需要在本地安装 Airflow. 建议你先选择一个 Python 版本并创建一个虚拟环境. 我们的开发都会在这个虚拟环境中进行.

Airflow 本身就是用 Python 写的, 所以它支持 ``pip install``. 但 Airflow 的依赖有一长串. 为了保证这些依赖互相之间不冲突, 你通常需要用 poetry 一类的 deterministic dependency management 工具来 resolve. Airflow 官方为不同的 airflow 版本以及不同的 Python 版本预先生成了一些依赖清单, 以 constrain file 的形式保存着. 你可以用下面这条命令安装 airflow 2.7.3 到 Python3.8 中:

.. code-block:: bash

    pip install "apache-airflow[celery]==2.7.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.8.txt"

当然你可以安装不同版本的 Airflow 到不同版本的 Python 中去, 你只需要改变 constrain file 即可. 这个 Constrain file 的 template 长这样子.

.. code-block:: bash

    https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt

- `Installation of Airflow <https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html>`_
- `Installation from PyPI <https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html>`_:


Verify the installation
------------------------------------------------------------------------------
以上的安装已经包含了 UI, Scheduler, Executor 的源代码了. 在生产环境中, 我们通常在不同的服务器上分别启用 UI, Scheduler (Executor 是由 Scheduler 启动的). 而在本地开发, 我们通常会用 ``aws standalone`` 命令一次性在本地全部将其启用. 这个命令还会自动创建一个 ``admin`` 用户, 并在 console 中打印出创建的密码. 例如我的用户密码是 ``username = admin, password = nsYA5wQeYnC8nbWC`` (你拿了没用, 因为这个环境在我的本地电脑上, 而且早就销毁了). 你可以用这个密码登录 UI. Airflow 可以用 CLI 来对 user 进行管理. 这些 user password 的信息是储存在 Airflow 数据库中的. 在本地开发模式下, 数据库是一个 sqlite, 在生产环境下是要用专门的高可用数据库的. 但是我们本地开发就不管这些了, 而是专注于业务代码的开发.

下面我们来验证安装是否成功了.

首先用 standalone 模式启动 airflow.

.. code-block:: bash

    airflow standalone

运行该命令后, 你会看到 ``Airflow is ready`` 的输出, 并且能在 http://0.0.0.0:8080/ 打开 UI 界面. 你还会看到 Airflow 自动创建了 ``${HOME}/airflow`` 文件. 里面有 ``airflow.cfg`` 文件是 Airflow 的配置. 而 ``airflow.db`` 则是 sqlite 数据库.

然后你打 ``airflow users list`` 命令列出所有的 user. 你会看到刚才自动创建的那个 admin user.

然后你打 ``airflow dags list`` 命令列出所有的 dag. 你安装 Airflow 后会自动安装一些示例的 dags. 所以你会看到一堆 Dag.

.. code-block:: bash

    airflow dags list


Write Your First DAG
------------------------------------------------------------------------------
这里给出了一个最简单, 只有一个 task 和一步, 并且 task 是一个简单的 Python 函数的例子.

.. literalinclude:: ../../../dags/dag1.py
   :language: python
   :linenos:

下面我还给出了一些最佳实践.

**在 Python 模块中而不是 DAG 中实现你的业务逻辑**

    在开发 DAG 的时候, 我建议把底层的业务逻辑放在你的 Python 模块中实现, 而不要放在 DAG 中. 你的 Python 模块应该对业务逻辑进行了充分的单元测试. 而 DAG 脚本主要负责只是把业务逻辑 import 进来调用, 并做一些读取 parameter 等杂活. 这样有助于保持你的代码库有序, 方便用测试 debug 你的业务逻辑.


Deploy Your DAG
------------------------------------------------------------------------------
对于本地 standalone 的 Airflow, 它会去 ``${AIRFLOW_HOME}/dags`` 这个路径下去找 python 文件. 如果有, 就尝试 import 进来, 如果成功 import 则视为部署完成, 你就可以开始启用并测试了. 这个 ``${AIRFLOW_HOME}`` 是在前节提到的的 ``${HOME}/airflow/airflow.cfg`` 中配置的. 默认就是 ``${HOME}/airflow``.

在本项目中, 我们把 dag 放在 git repo 中的 ``dags`` 目录下, 然后将其拷贝到 ``${HOME}/airflow/dags`` 即可. 这里我给出了一个自动化脚本, 它每秒都会扫描一次两个目录, 并尝试检查有没有不同, 有不同则自动拷贝过去.

.. literalinclude:: ../../../deploy_dags.py
   :language: python
   :linenos:

拷贝过去之后 airflow UI 里有一个选项是 auto-refresh. 它能自动去读 dags 目录并且 import dags. 但是这个功能的延迟比较高, 有时候甚至需要等 1 分钟看到新的 dag code. 我建议直接 Ctrl + C 杀死 Airflow 进程, 然后重新运行 ``airflow standalone`` 会比较方便. 毕竟是本地运行, 重启非常快.


Run DAG
------------------------------------------------------------------------------
你在 UI 中输入你的 dag id 应该能搜到你的 DAG. 注意, dag id 不是你的文件名, 而是你的 dag 入口函数中的 ``dag_id`` 参数的值.

1. 自动运行: 根据 dag 中的 schedule 定义, 由 Airflow 调度器来启动你的 dag run.
2. 在 UI 中手动运行: 在 UI 中手动点击 ``Trigger DAG`` (那个三角形播放按钮) 按钮来启动你的 dag run.
3. 用 CLI 运行: 使用 ``airflow dags trigger ${dag_id}`` 命令来启动你的 dag run. 如果你的 Airflow 在远程服务器上而你在本地, 则你需要一些配置工作.
