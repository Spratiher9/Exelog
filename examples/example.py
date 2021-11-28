"""

Example `exelog` usage

Run on spark, for example as follows:

    spark-submit --master local[2]  examples/example.py

"""

import logging

import pyspark

from exelog import enable_exelog

logger = logging.getLogger("example")


with_logging = enable_exelog(
    level=logging.INFO,
    format="[%(process)s/%(name)s] %(levelname)s %(message)s"
)

@with_logging
def process(x):
    logger.info("Got {x!r}".format(x=x))
    return x * x


def main():
    sc = pyspark.SparkContext.getOrCreate()
    logger.info("Spark context: {s!r}".format(s=sc))

    rdd = sc.parallelize(range(5))
    logger.info("RDD: {r!r}".format(r=rdd))

    result = rdd.map(process).collect()
    print(result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
