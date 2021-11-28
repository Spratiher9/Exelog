import pyspark

import exelog


def hello():
    print("Say Hello to the world!")


@exelog.initialized_call(hello)
def process(x):
    return x * x


def main():
    sc = pyspark.SparkContext.getOrCreate()
    result = sc.parallelize(range(100)).map(process).collect()
    print(result)


if __name__ == '__main__':
    main()
