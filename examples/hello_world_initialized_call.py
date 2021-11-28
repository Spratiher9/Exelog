"""

Example `exelog` usage

Run on spark, for example as follows:

    spark-submit --master local[2]  examples/hello_initialized_call.py

"""

import pyspark

from exelog import initialized_call


@initialized_call(lambda: print("hi world"))
def process(x):
    return x * x


def main():
    sc = pyspark.SparkContext.getOrCreate()
    result = sc.parallelize(range(5)).map(process).collect()
    print(result)


if __name__ == '__main__':
    main()
