from pyspark.sql import SparkSession
import os
		
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql-db")   # name of the MySQL Docker container
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")       # MySQL's default port (inside Docker network)
MYSQL_DB   = os.getenv("MYSQL_DB",   "salesdb")    # the database we created
MYSQL_USER = os.getenv("MYSQL_USER", "user")    # the user we created
#                         ↑
#              if you run python3 spark_job.py
#              directly in terminal without setting
#              any env variables — this default is used

MYSQL_PASS = os.getenv("MYSQL_PASS", "root")  # the password we set
#     │              │                   │
#  variable       read from           fallback if
#  in Python    Jenkins env block    not set anywhere



# 	Jenkinsfile                     spark_job.py
# ────────────────                ──────────────────────────────
# environment {         →  OS  →  os.getenv("MYSQL_HOST"):  returns "mysql-db"
#   MYSQL_HOST=mysql-db          
#   MYSQL_PORT=3306              os.getenv("MYSQL_PORT") : returns "3306"
#   MYSQL_DB=salesdb             os.getenv("MYSQL_DB") : returns salesdb
#   ...                          ...
# }

JAR_PATH = "/opt/spark-libs/mysql-connector.jar"


print("=" * 50)
print("Starting PySpark MySQL Reader")
print("=" * 50)

spark = SparkSession.builder \
	.appName("JenkinsPySparkDemo") \
    .config("spark.jars", JAR_PATH) \
    .config("spark.driver.extraClassPath", JAR_PATH) \
    .config("spark.executor.extraClassPath", JAR_PATH) \ 
	.getOrCreate()
	# Hardcoded '/opt/spark-libs/mysql-connector.jar' ==>  we created that path ourselves in the Download MySQL Driver stage in Jenkinsfile


spark.sparkContext.setLogLevel("ERROR")

jdbc_url = f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?useSSL=false&allowPublicKeyRetrieval=true"  # jdbc_url = "jdbc:mysql://mysql-db:3306/salesdb"
	
# +-------------------------------+----------+--------------------------------------------------+
# | Flag                          | Where    | What it does                                     |
# +-------------------------------+----------+--------------------------------------------------+
# | --ssl-mode=DISABLED           | mysqlCLI | tells mysql client to skip SSL entirely          |
# +-------------------------------+----------+--------------------------------------------------+
# | useSSL=false                  | JDBC URL | tells Spark/JDBC driver to skip SSL              |
# +-------------------------------+----------+--------------------------------------------------+
# | allowPublicKeyRetrieval=true  | JDBC URL | needed for MySQL 8.0 password auth without SSL   |
# +-------------------------------+----------+--------------------------------------------------+
print(f"Connecting to: {jdbc_url}")
print(f"Using jar: {JAR_PATH}") 

df = spark.read \
	.format("jdbc") \
	.option("url", jdbc_url) \
	.option("dbtable", "sales") \
	.option("user", MYSQL_USER) \
	.option("password", MYSQL_PASS) \
	.option("driver", "com.mysql.cj.jdbc.Driver") \
	.load()

print("\n--- Schema ---")
df.printSchema()

print("\n--- All Records ---")
df.show()

print(f"\nTotal records: {df.count()}")

spark.stop()
print("Done!")
