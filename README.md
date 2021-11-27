![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xlog)
[![PyPI](https://img.shields.io/pypi/v/xlog)](https://pypi.org/project/xlog/)

# xLog: Meticulous logging for Apache Spark
### _Enabling meticulous logging for Spark Applications_

`xLog` is a refactored logging module that provides a decorator based approach to ensure standard Python logging
from PySpark Executor nodes also.

## Why? 
### _The problem: logging from Spark executors doesn't work with Logging_

In Apache Spark, the actual data processing is done in what's called "executors", which are separate processes that 
are separate from the "driver" program. For end users, full control is only over the driver process, but not so much 
over the executor processes.

For example, in the PySpark driver program we can set up standard python logging as desired, but this setup is not
replicated in the executor processes. There are no out-of-the-box logging handlers for executors, so all logging 
messages from executors are lost. Since Python 3.2 however, when there are no handlers, there is still a "improvised" 
handler that will show `warning()` and `error()` messages in their bare format on standard error, but for proper
logging we probably need something more flexible and powerful than that.

Illustration in interactive PySpark shell:

    >>> import os, logging
    >>> logging.basicConfig(level=logging.INFO)
    
    >>> def describe():
    ...     return "pid: {p}, root handlers: {h}".format(p=os.getpid(), h=logging.root.handlers)
    ... 
    >>> describe()
    'pid: 8915, root handlers: [<StreamHandler <stderr> (NOTSET)>]'

    >>> sc.parallelize([4, 1, 7]).map(lambda x: describe()).collect()
    ['pid: 9111, root handlers: []', 'pid: 9128, root handlers: []', 'pid: 9142, root handlers: []']

The initial `describe()` happens in the driver and has root handlers because of the `basicConfig()` beforehand. However,
the `describe()` calls in the `map()` happen in separate executor processes (note the different PIDs) and got no 
root handlers.

## xLog: Logging Spark executor execution one decorator at a time

Various ways for setting up logging in your executors may be found on the internet. It usually entails sending 
and loading a separate file containing logging configuration code. Depending on your use case, managing this 
file may be difficult. One of the approaches is [here](https://community.cloudera.com/t5/Support-Questions/Logging-from-Pyspark-executor/td-p/212210)

In contrast, `epsel` takes a decorator based approach. You just have to decorate the data processing functions you are
passing to `map()`, `filter()`, `sortBy()`, etc.

A very minimal example:

    @epsel.ensure_info_logging
    def process(x):
        logger.info("Got {x}".format(x=x))
        return x * x
    
    result = rdd.map(process).collect()

What will happen here is that the first time `process()` is called in the executor, basic logging is set up with `INFO`
level, so that logging messages are not lost.

### Options and finetuning

The `ensure_basic_logging` decorator will do a basic logging setup using
[`logging.basicConfig()`](https://docs.python.org/3/library/logging.html#logging.basicConfig), and desired options can
be directly provided to the decorator as illustrated in the following example using the interactive PySpark shell:

    >>> import logging
    >>> from epsel import ensure_basic_logging
    >>> logger = logging.getLogger("example")
    
    >>> @ensure_basic_logging(level=logging.INFO)
    ... def process(x):
    ...     logger.info("Got {x}".format(x=x))
    ...     return x * x
    ... 
    >>> sc.parallelize(range(5)).map(process).collect()
    INFO:example:Got 0
    INFO:example:Got 1
    INFO:example:Got 3
    INFO:example:Got 2
    INFO:example:Got 4
    [0, 1, 4, 9, 16]

To improve readability or code reuse, you can of course predefine decorators:

    with_logging = ensure_basic_logging(
        level=logging.INFO,
        format="[%(process)s/%(name)s] %(levelname)s %(message)s"
    )
    
    @with_logging
    def process(x):
        ...

`epsel` also defines some simple predefined decorators:

    # Predefined decorator for stderr/INFO logging
    ensure_info_logging = ensure_basic_logging(level=logging.INFO)
    
    # Predefined decorator for stderr/DEBUG logging
    ensure_debug_logging = ensure_basic_logging(level=logging.DEBUG)

### Fine-grained logging set up

If the `logging.basicConfig()` API is not flexible enough for your desired setup, you can also inject more advanced
setup code with the `on_first_time` decorator. This decorator is not limited to logging setup, it just expects a
callable (that can be called without arguments). A very simple example:

    @epsel.on_first_time(lambda: print("hello world"))
    def process(x):
        ....

This will print "hello world" the first time the `process` function is called in each executor.
