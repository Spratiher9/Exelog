import logging
import subprocess
import unittest.mock as mock
from io import StringIO
from pathlib import Path

import pytest

import exelog


def test_initialized_call():
    history = []

    def intro():
        history.append("hello world")

    @exelog.initialized_call(intro)
    def process(x):
        history.append(x)

    for x in range(5):
        process(x)

    assert history == ["hello world", 0, 1, 2, 3, 4]


def test_enable_exelog_no_params():
    with mock.patch('logging.basicConfig') as basicConfig:
        @exelog.enable_exelog
        def process(x):
            return x * 2

        basicConfig.assert_not_called()
        process(1)
        basicConfig.assert_called_once_with()
        process(2)
        basicConfig.assert_called_once_with()
        process(3)
        basicConfig.assert_called_once_with()


def test_enable_exelog_params():
    with mock.patch('logging.basicConfig') as basicConfig:
        fmt = "%(message)s"
        lvl = logging.INFO

        @exelog.enable_exelog(level=lvl, format=fmt)
        def process(x):
            return x * 2

        basicConfig.assert_not_called()
        process(1)
        basicConfig.assert_called_once_with(level=lvl, format=fmt)
        process(2)
        basicConfig.assert_called_once_with(level=lvl, format=fmt)


def test_enable_exelog_output():
    with mock.patch(
            'logging.root', new=logging.RootLogger(level=logging.INFO)
    ) as root:
        # Root handlers must be empty for basicConfig to do anything
        assert logging.root.handlers == []

        buffer = StringIO()
        fmt = "%(levelname)s:%(name)s:%(message)s"

        @exelog.enable_exelog(level=logging.INFO, format=fmt,
                              stream=buffer)
        def process(x):
            root.info("Got {x!r}".format(x=x))
            return x * 2

        assert buffer.getvalue() == ""
        process(1)
        assert buffer.getvalue() == "INFO:root:Got 1\n"
        process(2)
        assert buffer.getvalue() == "INFO:root:Got 1\nINFO:root:Got 2\n"
        process(3)
        assert buffer.getvalue() == "INFO:root:Got 1\nINFO:root:Got 2\nINFO:root:Got 3\n"


def run_job(filename, workers=2):
    command = [
        "spark-submit",
        "--master=local[{w}]".format(w=workers),
        str(Path(__file__).parent / filename)
    ]
    print(command)
    res = subprocess.run(
        command,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=60
    )
    print("returncode", res.returncode)
    print("stdout", res.stdout)
    print("stderr", res.stderr)
    return res


@pytest.mark.parametrize("workers", [1, 2, 4])
def test_job_say_hello(workers):
    res = run_job("job_say_hello.py", workers=workers)
    assert res.returncode == 0
    assert res.stderr.count(b"Hello world!") == workers
    assert res.stdout.startswith(b"[0, 1, 4, 9, 16, 25")


def test_job_log_process():
    res = run_job("job_log_process.py")
    assert res.returncode == 0
    for x in range(5):
        expected = "___ job_log_process INFO Processing {x}".format(x=x)
        assert expected.encode('utf-8') in res.stderr
    assert res.stdout == b"___ job_log_process INFO Result: [0, 1, 4, 9, 16]\n"
