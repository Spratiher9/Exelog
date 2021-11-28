[comment]: <> (<a href="https://ibb.co/jhTdDPZ"><img src="https://i.ibb.co/6Ym2F7J/xLogs.gif" alt="Exelog: Meticulous logging for Apache Spark" border="0"></a>)

![Exelog: Meticulous logging for Apache Spark](https://raw.githubusercontent.com/Spratiher9/Files/master/xLogs.gif)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/exelog)
[![PyPI](https://img.shields.io/pypi/v/exelog)](https://pypi.org/project/exelog/)

# Exelog: Meticulous logging for Apache Spark

### _Enabling meticulous logging for Spark Applications_

`Exelog` is a refactored logging module that provides a decorator based approach to ensure standard Python logging from
PySpark Executor nodes also.

### Installation

```shell
pip install exelog
```

## Why?

### _The problem: logging from Spark executors doesn't work with normal logging_

In Apache Spark, the actual data processing is done in what's called "executors", which are separate processes that are
separate from the "driver" program. For end users, full control is only over the driver process, but not so much over
the executor processes.

For example, in the PySpark driver program we can set up standard python logging as desired, but this setup is not
replicated in the executor processes. There are no out-of-the-box logging handlers for executors, so all logging
messages from executors are lost. Since Python 3.2 however, when there are no handlers, there is still a "improvised"
handler that will show `warning()` and `error()` messages in their bare format on standard error, but for proper logging
we probably need something more flexible and powerful than that.

Illustration in interactive PySpark shell:
```python
    >>> import os, logging
    >>> logging.basicConfig(level=logging.INFO)
    
    >>> def describe():
    ...     return "pid: {p}, root handlers: {h}".format(p=os.getpid(), h=logging.root.handlers)
    ... 
    >>> describe()
    'pid: 8915, root handlers: [<StreamHandler <stderr> (NOTSET)>]'

    >>> sc.parallelize([4, 1, 7]).map(lambda x: describe()).collect()
    ['pid: 9111, root handlers: []', 'pid: 9128, root handlers: []', 'pid: 9142, root handlers: []']
```
The initial `describe()` happens in the driver and has root handlers because of the `basicConfig()` beforehand. However,
the `describe()` calls in the `map()` happen in separate executor processes (note the different PIDs) and got no root
handlers.

## Exelog: Logging Spark executor execution one decorator at a time

Various ways for setting up logging for executors may be found on the internet. It usually entails sending and loading a
separate file containing logging configuration code. Depending on the use case, managing this file may be difficult. One
of the approaches
is [here](https://community.cloudera.com/t5/Support-Questions/Logging-from-Pyspark-executor/td-p/212210)

In contrast, `Exelog` takes a decorator based approach. We just have to decorate the data processing functions which we
are passing to `map()`, `filter()`, `sortBy()`, etc.

A very minimal example:
```python
    @exelog.enable_info_logging
    def process(x):
        logger.info("Got {x}".format(x=x))
        return x * x
    
    result = rdd.map(process).collect()
```
What will happen here is that the first time `process()` is called in the executor, basic logging is set up with `INFO`
level, so that logging messages are not lost.

### Options and finetuning

The `enable_exelog` decorator will do a basic logging setup using
[`logging.basicConfig()`](https://docs.python.org/3/library/logging.html#logging.basicConfig), and desired options can
be directly provided to the decorator as illustrated in the following example using the interactive PySpark shell:
```python
    >>> import logging
    >>> from exelog import enable_exelog
    >>> logger = logging.getLogger("example")
    
    >>> @enable_exelog(level=logging.INFO)
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
```
To improve readability or code reuse, you can of course predefine decorators:
```python
    with_logging = enable_exelog(
        level=logging.INFO,
        format="[%(process)s/%(name)s] %(levelname)s %(message)s"
    )
    
    @with_logging
    def process(x):
        ...
```
`exelog` also defines some simple predefined decorators:
```python
    # Predefined decorator for stderr/NOTSET logging
    enable_notset_logging = enable_exelog(level=logging.NOTSET)
    
    # Predefined decorator for stderr/DEBUG logging
    enable_debug_logging = enable_exelog(level=logging.DEBUG)
    
    # Predefined decorator for stderr/INFO logging
    enable_info_logging = enable_exelog(level=logging.INFO)
    
    # Predefined decorator for stderr/WARN logging
    enable_warn_logging = enable_exelog(level=logging.WARN)
    
    # Predefined decorator for stderr/ERROR logging
    enable_error_logging = enable_exelog(level=logging.ERROR)
    
    # Predefined decorator for stderr/CRITICAL logging
    enable_critical_logging = enable_exelog(level=logging.CRITICAL)
```
### Fine-grained logging set up

If the `logging.basicConfig()` API is not flexible enough for your desired setup, you can also inject more advanced
setup code with the `initialized_call` decorator. This decorator is not limited to logging setup, it just expects a
callable (that can be called without arguments). A very simple example:

    @exelog.initialized_call(lambda: print("Executor logging enabled"))
    def process(x):
        ....

This will print "Executor logging enabled" the first time the `process` function is called in each executor.
