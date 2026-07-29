from pathlib import Path

import pytest
from pyspark.sql import SparkSession

from src.pipeline import EVENT_SCHEMA, build_gold, transform_silver


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("TelecomPipelineTests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_silver_deduplicates_and_filters_invalid_events(spark: SparkSession) -> None:
    rows = [
        (
            "evt-1",
            "SUB-10001",
            "2026-07-20T10:00:00",
            "Chicago",
            "CHI-101",
            "DROPPED_CALL",
            -110.0,
            175.0,
            0,
        ),
        (
            "evt-1",
            "SUB-10001",
            "2026-07-20T10:00:00",
            "Chicago",
            "CHI-101",
            "DROPPED_CALL",
            -110.0,
            175.0,
            0,
        ),
        (
            "evt-2",
            "SUB-10002",
            "2026-07-20T11:00:00",
            "Chicago",
            "CHI-102",
            "UNKNOWN",
            -90.0,
            40.0,
            0,
        ),
    ]

    bronze_df = spark.createDataFrame(rows, EVENT_SCHEMA)
    silver_df = transform_silver(bronze_df)

    assert silver_df.count() == 1

    record = silver_df.first()
    assert record["is_dropped_call"] == 1
    assert record["is_poor_quality"] == 1
    assert record["quality_status"] == "POOR"


def test_gold_calculates_drop_rate(spark: SparkSession) -> None:
    rows = [
        (
            "evt-1",
            "SUB-10001",
            "2026-07-20T10:00:00",
            "Chicago",
            "CHI-101",
            "DROPPED_CALL",
            -110.0,
            175.0,
            0,
        ),
        (
            "evt-2",
            "SUB-10002",
            "2026-07-20T11:00:00",
            "Chicago",
            "CHI-101",
            "CALL_END",
            -90.0,
            40.0,
            0,
        ),
    ]

    silver_df = transform_silver(spark.createDataFrame(rows, EVENT_SCHEMA))
    gold_record = build_gold(silver_df).first()

    assert gold_record["total_events"] == 2
    assert gold_record["dropped_calls"] == 1
    assert gold_record["drop_rate_pct"] == 50.0
