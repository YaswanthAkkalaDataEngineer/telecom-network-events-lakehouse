from __future__ import annotations

from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
)

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "data" / "sample" / "network_events.csv"
OUTPUT_PATH = BASE_DIR / "output"

VALID_EVENT_TYPES = [
    "CALL_START",
    "CALL_END",
    "DATA_SESSION",
    "DROPPED_CALL",
]

EVENT_SCHEMA = StructType(
    [
        StructField("event_id", StringType(), False),
        StructField("subscriber_id", StringType(), False),
        StructField("event_time", StringType(), False),
        StructField("region", StringType(), False),
        StructField("cell_tower_id", StringType(), False),
        StructField("event_type", StringType(), False),
        StructField("signal_strength_dbm", DoubleType(), True),
        StructField("latency_ms", DoubleType(), True),
        StructField("bytes_used", LongType(), True),
    ]
)


def create_spark_session() -> SparkSession:
    """Create a local Spark session for the prototype."""
    return (
        SparkSession.builder
        .appName("TelecomNetworkEventsLakehouse")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def load_bronze(spark: SparkSession, input_path: Path = INPUT_PATH) -> DataFrame:
    """Read raw network events and attach ingestion metadata."""
    return (
        spark.read
        .option("header", True)
        .schema(EVENT_SCHEMA)
        .csv(str(input_path))
        .withColumn("ingested_at", F.current_timestamp())
        .withColumn("source_file", F.input_file_name())
    )


def transform_silver(bronze_df: DataFrame) -> DataFrame:
    """Clean, validate, deduplicate, and enrich Bronze records."""
    return (
        bronze_df
        .withColumn(
            "event_timestamp",
            F.to_timestamp("event_time", "yyyy-MM-dd'T'HH:mm:ss"),
        )
        .filter(F.col("event_id").isNotNull())
        .filter(F.col("subscriber_id").isNotNull())
        .filter(F.col("cell_tower_id").isNotNull())
        .filter(F.col("event_timestamp").isNotNull())
        .filter(F.col("event_type").isin(VALID_EVENT_TYPES))
        .dropDuplicates(["event_id"])
        .withColumn("event_date", F.to_date("event_timestamp"))
        .withColumn(
            "is_dropped_call",
            F.when(F.col("event_type") == "DROPPED_CALL", F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "is_poor_quality",
            F.when(
                (F.col("signal_strength_dbm") < -105)
                | (F.col("latency_ms") > 150),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "quality_status",
            F.when(F.col("is_poor_quality") == 1, F.lit("POOR"))
            .otherwise(F.lit("GOOD")),
        )
    )


def build_gold(silver_df: DataFrame) -> DataFrame:
    """Aggregate business-ready daily network KPIs."""
    return (
        silver_df
        .groupBy("event_date", "region", "cell_tower_id")
        .agg(
            F.count("*").alias("total_events"),
            F.sum("is_dropped_call").alias("dropped_calls"),
            F.round(F.avg("signal_strength_dbm"), 2).alias("avg_signal_strength_dbm"),
            F.round(F.avg("latency_ms"), 2).alias("avg_latency_ms"),
            F.sum("is_poor_quality").alias("poor_quality_events"),
            F.sum(F.coalesce(F.col("bytes_used"), F.lit(0))).alias("total_bytes_used"),
        )
        .withColumn(
            "drop_rate_pct",
            F.round((F.col("dropped_calls") / F.col("total_events")) * 100, 2),
        )
        .orderBy("event_date", "region", "cell_tower_id")
    )


def build_quality_report(bronze_df: DataFrame, silver_df: DataFrame) -> DataFrame:
    """Create a compact pipeline-level data-quality report."""
    bronze_count = bronze_df.count()
    silver_count = silver_df.count()

    return bronze_df.sparkSession.createDataFrame(
        [
            (
                bronze_count,
                silver_count,
                bronze_count - silver_count,
                round(((bronze_count - silver_count) / bronze_count) * 100, 2)
                if bronze_count
                else 0.0,
            )
        ],
        ["bronze_rows", "silver_rows", "rejected_or_duplicate_rows", "rejection_rate_pct"],
    )


def write_outputs(
    bronze_df: DataFrame,
    silver_df: DataFrame,
    gold_df: DataFrame,
    quality_df: DataFrame,
    output_path: Path = OUTPUT_PATH,
) -> None:
    """Write partitioned prototype outputs."""
    bronze_df.write.mode("overwrite").parquet(str(output_path / "bronze"))

    (
        silver_df.write
        .mode("overwrite")
        .partitionBy("event_date")
        .parquet(str(output_path / "silver"))
    )

    (
        gold_df.write
        .mode("overwrite")
        .partitionBy("event_date")
        .parquet(str(output_path / "gold"))
    )

    quality_df.write.mode("overwrite").json(str(output_path / "quality"))


def main() -> None:
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    try:
        bronze_df = load_bronze(spark)
        silver_df = transform_silver(bronze_df)
        gold_df = build_gold(silver_df)
        quality_df = build_quality_report(bronze_df, silver_df)

        write_outputs(bronze_df, silver_df, gold_df, quality_df)

        print("\nGold network KPI preview:")
        gold_df.show(truncate=False)

        print("\nData-quality summary:")
        quality_df.show(truncate=False)

        print(f"\nPipeline completed. Output written to: {OUTPUT_PATH}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
