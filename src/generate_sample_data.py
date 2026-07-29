from __future__ import annotations

import argparse
import csv
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = BASE_DIR / "data" / "sample" / "network_events.csv"

REGIONS = ["Chicago", "Dallas", "Atlanta", "New York"]
TOWERS = {
    "Chicago": ["CHI-101", "CHI-102", "CHI-103"],
    "Dallas": ["DAL-201", "DAL-202", "DAL-203"],
    "Atlanta": ["ATL-301", "ATL-302", "ATL-303"],
    "New York": ["NYC-401", "NYC-402", "NYC-403"],
}
EVENT_TYPES = ["CALL_START", "CALL_END", "DATA_SESSION", "DROPPED_CALL"]


def generate_rows(row_count: int) -> list[dict[str, object]]:
    random.seed(42)
    start_time = datetime.now(timezone.utc) - timedelta(days=7)
    rows: list[dict[str, object]] = []

    for _ in range(row_count):
        region = random.choice(REGIONS)
        event_type = random.choices(
            EVENT_TYPES,
            weights=[30, 30, 32, 8],
            k=1,
        )[0]

        rows.append(
            {
                "event_id": str(uuid.uuid4()),
                "subscriber_id": f"SUB-{random.randint(10000, 99999)}",
                "event_time": (
                    start_time + timedelta(seconds=random.randint(0, 604800))
                ).strftime("%Y-%m-%dT%H:%M:%S"),
                "region": region,
                "cell_tower_id": random.choice(TOWERS[region]),
                "event_type": event_type,
                "signal_strength_dbm": round(random.uniform(-125, -65), 2),
                "latency_ms": round(random.uniform(15, 260), 2),
                "bytes_used": (
                    random.randint(1000, 25_000_000)
                    if event_type == "DATA_SESSION"
                    else 0
                ),
            }
        )

    # Add one duplicate record to demonstrate deduplication.
    if rows:
        rows.append(rows[0].copy())

    return rows


def write_csv(rows: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "event_id",
        "subscriber_id",
        "event_time",
        "region",
        "cell_tower_id",
        "event_type",
        "signal_strength_dbm",
        "latency_ms",
        "bytes_used",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic telecom events.")
    parser.add_argument("--rows", type=int, default=500)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.rows <= 0:
        raise ValueError("--rows must be greater than zero.")

    rows = generate_rows(args.rows)
    write_csv(rows, args.output)
    print(f"Generated {len(rows)} rows at {args.output}")


if __name__ == "__main__":
    main()
