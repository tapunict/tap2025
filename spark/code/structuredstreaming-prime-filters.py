from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.functions import udf
from pyspark.sql.types import BooleanType

@udf(returnType=BooleanType())
def isprime(n):
    """
    check if integer n is a prime
    """
    #print(n)
    #return True
    # make sure n is a positive integer
    n = abs(int(n))
    # 0 and 1 are not primes
    if n < 2:
        return False
    # 2 is the only even prime number
    if n == 2:
        return True
    # all other even numbers are not primes
    if not n & 1:
        return False
    # range starts with 3 and only needs to go up the square root of n
    # for all odd numbers
    for x in range(3, int(n**0.5)+1, 2):
        if n % x == 0:
            return False
    return True

# Create a Spark Session 

spark = SparkSession \
    .builder \
    .appName("StructuredNetworkWordCount") \
    .getOrCreate()


# To reduce verbose output
spark.sparkContext.setLogLevel("ERROR") 

# Create DataFrame reading from Rate Source
df = spark \
    .readStream \
    .format("rate") \
    .option("rowsPerSecond", 100000) \
    .load()

# Rate source produces these data
#+--------------------+-----+
#|           timestamp|value|
#+--------------------+-----+
#|2023-05-07 16:16:...|  500|
#|2023-05-07 16:16:...|  508|

# Let's take the "primes" signals aèèlying a filter using an udf function

primes = df.filter(isprime('value'))

# Start running the query that prints the running counts to the console
query = primes \
    .writeStream \
    .format("console") \
    .start()

query.awaitTermination()

