# Architecture Notes

## Portfolio Goal

This prototype shows the design decisions expected from a senior data engineer without exposing any proprietary implementation.

## Data Flow

1. A synthetic generator creates telecom network-event records.
2. Bronze preserves raw source values and adds ingestion metadata.
3. Silver validates keys, timestamps, event types, and duplicate event IDs.
4. Silver adds network-quality flags for dropped calls, weak signal, and latency.
5. Gold aggregates daily KPIs by region and tower.
6. A quality report compares raw and accepted row counts.

## Cloud Mapping

| Prototype Component | AWS | Azure | GCP |
|---|---|---|---|
| Raw storage | S3 | ADLS Gen2 | Cloud Storage |
| Processing | EMR/Glue/Databricks | Azure Databricks | Dataproc/Databricks |
| Orchestration | MWAA/Step Functions | ADF | Cloud Composer |
| Warehouse | Redshift | Synapse | BigQuery |
| Streaming extension | MSK/Kinesis | Event Hubs | Pub/Sub |
| Monitoring | CloudWatch | Azure Monitor | Cloud Monitoring |

## Security and Governance Discussion

A production version should include:

- Encryption in transit and at rest
- Least-privilege IAM or RBAC
- Secrets stored outside source control
- Dataset ownership and retention rules
- Column-level masking for sensitive attributes
- Data lineage and audit logging
- SLA monitoring and incident alerts
