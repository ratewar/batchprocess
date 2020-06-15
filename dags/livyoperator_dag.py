from __future__ import print_function
from airflow.operators import LivySparkOperator
from airflow.models import DAG
from datetime import datetime, timedelta
import os

"""
Pre-run Steps:
1. Open the Airflow WebServer
2. Navigate to Admin -> Connections
3. Add a new connection
    1. Set the Conn Id as "livy_http_conn"
    2. Set the Conn Type as "http"
    3. Set the host
    4. Set the port (default for livy is 8998)
    5. Save
"""

DAG_ID = os.path.basename(__file__).replace(".pyc", "").replace(".py", "")

HTTP_CONN_ID = "livy_http_conn"
SESSION_TYPE = "spark"
SPARK_SCRIPT = """
import java.util
println("sc: " + sc)
val rdd = sc.parallelize(1 to 5)
val rddFiltered = rdd.filter(entry => entry > 3)
println(util.Arrays.toString(rddFiltered.collect()))
val movies_df = spark.read.format("csv").option("header", "true").option("inferschema", "true").load("s3://batchmovielensdataset/movies.csv")
movies_df.write.mode("overwrite").parquet("s3://batchmovielensdataset/movielens-parquet/movies/")
"""

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
    }

dag = DAG(DAG_ID, default_args=default_args, schedule_interval=None, start_date=(datetime.now() - timedelta(minutes=1)))

dummy = LivySparkOperator(
    task_id='livy-' + SESSION_TYPE,
    spark_script=SPARK_SCRIPT,
    http_conn_id=HTTP_CONN_ID,
    session_kind=SESSION_TYPE,
    dag=dag)