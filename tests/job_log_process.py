import logging

import pyspark

from exelog import enable_exelog

LOG_FORMAT = "___ %(name)s %(levelname)s %(message)s"
logger = logging.getLogger("job_log_process")


@enable_exelog(level=logging.INFO, format=LOG_FORMAT)
def process(x):
    logger.info("Processing {x}".format(x=x))
    return x * x


def main():
    sc = pyspark.SparkContext.getOrCreate()
    result = sc.parallelize(range(5)).map(process).collect()
    logger.info("Result: {r!r}".format(r=result))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    main()
