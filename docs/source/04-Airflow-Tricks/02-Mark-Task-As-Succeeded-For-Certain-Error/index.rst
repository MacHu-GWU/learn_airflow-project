.. _mark-task-as-succeeded-for-certain-error:

Mark Task as Succeeded for Certain Error
==============================================================================


Overview
------------------------------------------------------------------------------
在生产环境中我们可能会遇到以下问题:

    有的时候一个 task 抛出的异常在逻辑上并不是 task 本身的错误, 可能是外部环境的错误. 我们希望对其进行处理之后判断这是不是真的是一个错误. 如果不是, 我们希望将这个 task 标记为成功, 而不是失败.

这个问题的本质是把 task 本身当做一个黑盒, 对其进行异常处理. 我们知道, 在 Python 中异常处理是用 ``try ... except ...`` 实现的. 在 airflow 中, 你的 task 业务逻辑需要被封装成 Python 函数, 而你要用 `Operator <https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html>`_ 把你的 Python 函数封装成一个 task. 这个 Operator 能将异常处理, 重试, 打日志, Context, 处理输入输出等等功能封装起来. 所以这件事的关键是对 Operator 的执行逻辑进行异常处理.


If you use PythonOperator
------------------------------------------------------------------------------
如果你的 task 是用 `PythonOperator <https://airflow.apache.org/docs/apache-airflow/stable/howto/operator/python.html>`_ 封装的. 那么这比较简单, 你只需要把你的业务逻辑的 Python 函数用另一个函数封装起来, 并加上 ``try ... except ...``, 然后在 except 中进行处理即可.


If you use Other Operator
------------------------------------------------------------------------------
而如果你的 task 是用的第三方的 Operator 封装的, 不存在指定一个 Python 函数作为业务逻辑的情况. 事情就比较复杂了. 例如你用 `AwsLambdaInvokeFunctionOperator <https://airflow.apache.org/docs/apache-airflow-providers-amazon/3.1.1/operators/lambda.html>`_ 来运行一个 AWS Lambda 函数. 这个 Operator 并没有一段程序作为业务逻辑, 我们也就无法对其进行 ``try ... except ...`` 异常处理了. 那这种情况该怎么办呢?

答案是, 继承原有 Operator 的类, 并对原有的 ``def execute(self, context: Context)`` 进行封装. Airflow 所有的 Operator 都是继承自 `BaseOperator <https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/baseoperator/index.html#airflow.models.baseoperator.BaseOperator>`_ 的. 它有一个 ``execute`` 的方法, 其中的逻辑是对真正的业务逻辑利用 `Hook <https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/connections.html#hooks>`_ 钩子封装并处理从而能跟 `Connection <https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html>`_ 结合. 这里我们不展开说 Hook 和 Connection, 只要知道 ``execute`` 方法是这里的关键即可.

不管我们的 task 中有什么错误, 它都是在 execute 方法中被 raise 出来的. 那么我们只需要在子类中 override 这个, 然后用 ``try ... except ...`` 把 ``return super().execute(context)`` 封装起来即可. 具体逻辑如下:

1. 如果成功, 那么原来返回什么我们还是返回什么.
2. 如果失败, 并且是我们需要特别处理的 Exception, 那么我们处理之后并返回一个跟原本需要返回的值数据结构类似, 但是能反映出来这个 task 是由异常的值即可. 这个值需要能 JSON serializable.
3. 如果失败, 并且是未知的异常, 那么原地 raise 即可.

请看下面的示例代码.

.. code-block:: python

    from airflow.providers.path.to.your.operator import ThirdPartyOperator

    class MyOperator(ThirdPartyOperator):
        def execute(self, context):
            try:
                return super().execute(context)
            except MyImportantException as e:
                print(f"encounter MyImportantException, which is OK")
                return "OK"
            except Exception as e:
                raise e

这里我们就哪 ``AwsLambdaInvokeFunctionOperator`` 举例. 下面是 ``AwsLambdaInvokeFunctionOperator.execute(...)`` 的源代码. 你可以看到里面的本质是用 hook 这里 ``self.hook.invoke_lambda(...)`` 调用 boto3 API, 然后对 response 进行处理后再返回 payload.

.. code-block:: python

    def execute(self, context: Context):
        """
        Invoke the target AWS Lambda function from Airflow.

        :return: The response payload from the function, or an error object.
        """
        success_status_codes = [200, 202, 204]
        self.log.info("Invoking AWS Lambda function: %s with payload: %s", self.function_name, self.payload)
        response = self.hook.invoke_lambda(
            function_name=self.function_name,
            invocation_type=self.invocation_type,
            log_type=self.log_type,
            client_context=self.client_context,
            payload=self.payload,
            qualifier=self.qualifier,
        )
        self.log.info("Lambda response metadata: %r", response.get("ResponseMetadata"))

        if log_result := response.get("LogResult"):
            log_records = self.hook.encode_log_result(
                log_result,
                keep_empty_lines=self.keep_empty_log_lines,
            )
            if log_records:
                self.log.info(
                    "The last 4 KB of the Lambda execution log (keep_empty_log_lines=%s).",
                    self.keep_empty_log_lines,
                )
                for log_record in log_records:
                    self.log.info(log_record)

        if response.get("StatusCode") not in success_status_codes:
            raise ValueError("Lambda function did not execute", json.dumps(response.get("ResponseMetadata")))
        payload_stream = response.get("Payload")
        payload = payload_stream.read().decode()
        if "FunctionError" in response:
            raise ValueError(
                "Lambda function execution resulted in error",
                {"ResponseMetadata": response.get("ResponseMetadata"), "Payload": payload},
            )
        self.log.info("Lambda function invocation succeeded: %r", response.get("ResponseMetadata"))
        return payload

假设我们希望在 AWS Lambda 的 capacity 不足的情况不抛出异常, 因为 capacity 不足并不意味着有什么错误, 我们之后重试就可以了 那么我们的解决方案也很简单. 如果它遇到了 ``InsufficientCapacityException`` (这是我编的, 举个例子而已), 因为原来的返回值是 payload, 那么我我们依然返回一个 payload, 但是里面的内容表示异常不足即可. 示例代码如下:

.. code-block:: python

    def execute(self, context):
        try:
            return super().execute(context)
        except InsufficientCapacityException as e:
            print(f"encounter MyImportantException, which is OK")
            return "InsufficientCapacityException"
        except Exception as e:
            raise e

这个方法可以说是通用的, 适用于任何 operator.

下面我们给出了一个示例 dag:

.. dropdown:: dag_0003_mark_task_as_succeeded_for_certain_error.py

    .. literalinclude:: ../../../../dags/dag_0003_mark_task_as_succeeded_for_certain_error.py
       :language: python
       :linenos:

最终的 Log 如下::

    [2024-01-11, 20:49:11 UTC] {logging_mixin.py:154} INFO - Start task1
    [2024-01-11, 20:49:11 UTC] {logging_mixin.py:154} INFO - encounter MyCustomException, which is OK


Subsequent Tasks
------------------------------------------------------------------------------
上一个方法很完美, 非常通用且自定义程度很高. 但是这里仍然有一个问题没有解决. 在 DAG 中, 你这个被重点关注的 task 后续可能还有其他 task, 它们依赖于这个 task 的返回数据. 如果你的 task 返回了一个异常, 那么后续的 task 就会接到错误的数据而导致无法正常执行. 这个问题该如何解决呢?

答案也很简单. 在重点 task 之后接一个 PythonOperator 的 task, 对返回值进行处理. 如果收到的是正常数据则继续进行, 如果是错误数据则提前终止整个 dag. Airflow 官方的 `ShortCircuitOperator <https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/python/index.html#airflow.operators.python.ShortCircuitOperator>`_ 就是干这件事的.

这里提一下一个常见的错误方案. 很多人会希望在异常处理的逻辑中对 context 对象进行修改. 然后再后续的 task 中都加上 ``if context["should_i_run_xyz"]`` 这样的判断逻辑来根据前面的 task 输出决定自己是不是要运行. 这样做可行, 但是极不推荐. 因为这样对代码侵入性很大, 你为了解决一个 task 的问题, 导致要修改所有后续 task, 非常不可持续.


Why Callback Won't Work
------------------------------------------------------------------------------
Airflow 中有一些 `Callback <https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/callbacks.html>`_, 可以在特定事件发生时自动运行你的自定义函数. 例如你可以用在 task failed 的时候运行 ``on_failure_callback`` 函数.

我开始尝试用这个方法来解决, 但是行不通. 因为 callback 是发生在 task 被标记为 failed 之后的, 你在 callback 中无论怎么做都无法改变 task 的状态. 就算可以, 这样做也很违背设计模式, 很容易滥用这一机制. 所以我最终放弃了这个方法.


Summary
------------------------------------------------------------------------------
本文介绍了如果把 task 作为一个黑盒对其进行异常处理的方法.
