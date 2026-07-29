from pathlib import Path
from pyspark.sql import SparkSession,functions as F
ROOT=Path(__file__).resolve().parents[1]
spark=SparkSession.builder.appName('TelecomNetworkPrototype').master('local[*]').getOrCreate()
cdr=spark.read.option('header',True).option('inferSchema',True).csv(str(ROOT/'data/raw/cdr/cdr.csv'))
silver=(cdr.withColumn('event_timestamp',F.to_timestamp('call_start_time')).withColumn('event_date',F.to_date('event_timestamp')).dropDuplicates(['cdr_id']).withColumn('is_dropped_call',F.when(F.col('call_status')=='DROPPED',1).otherwise(0)).withColumn('is_poor_quality',F.when((F.col('signal_strength_dbm')<-105)|(F.col('latency_ms')>150),1).otherwise(0)))
gold=(silver.groupBy('event_date','region','source_tower_id').agg(F.count('*').alias('total_calls'),F.sum('is_dropped_call').alias('dropped_calls'),F.round(F.avg('latency_ms'),2).alias('avg_latency_ms'),F.round(F.avg('signal_strength_dbm'),2).alias('avg_signal_strength_dbm'),F.sum('is_poor_quality').alias('poor_quality_calls')).withColumn('drop_rate_pct',F.round(F.col('dropped_calls')/F.col('total_calls')*100,2)))
gold.show(20,False); spark.stop()
