# Data Dictionary

## cdr

Path: `data/raw/cdr/cdr.csv`  
Primary key: `cdr_id`

| Column | Required |
|---|---|
| `cdr_id` | Yes |
| `subscriber_id` | Yes |
| `call_start_time` | Yes |
| `call_end_time` | Yes |
| `duration_seconds` | Yes |
| `source_tower_id` | Yes |
| `destination_tower_id` | Yes |
| `call_type` | Yes |
| `call_status` | Yes |
| `roaming_flag` | Yes |
| `network_type` | Yes |
| `signal_strength_dbm` | Yes |
| `latency_ms` | Yes |
| `region` | Yes |

## network_events

Path: `data/raw/network_events/network_events.csv`  
Primary key: `event_id`

| Column | Required |
|---|---|
| `event_id` | Yes |
| `event_time` | Yes |
| `tower_id` | Yes |
| `event_type` | Yes |
| `severity` | Yes |
| `latency_ms` | Yes |
| `packet_loss_pct` | Yes |
| `signal_strength_dbm` | Yes |
| `utilization_pct` | Yes |
| `availability_pct` | Yes |
| `region` | Yes |

## subscriber_activity

Path: `data/raw/subscriber_activity/subscriber_activity.csv`  
Primary key: `activity_id`

| Column | Required |
|---|---|
| `activity_id` | Yes |
| `subscriber_id` | Yes |
| `activity_time` | Yes |
| `activity_type` | Yes |
| `data_usage_mb` | Yes |
| `device_type` | Yes |
| `network_type` | Yes |
| `roaming_flag` | Yes |
| `tower_id` | Yes |
| `region` | Yes |

## cell_towers

Path: `data/raw/reference/cell_towers.csv`  
Primary key: `tower_id`

| Column | Required |
|---|---|
| `tower_id` | Yes |
| `region` | Yes |
| `city` | Yes |
| `latitude` | Yes |
| `longitude` | Yes |
| `capacity_sessions` | Yes |
| `commissioned_date` | Yes |
| `technology` | Yes |
| `status` | Yes |

## service_tickets

Path: `data/raw/operations/service_tickets.csv`  
Primary key: `ticket_id`

| Column | Required |
|---|---|
| `ticket_id` | Yes |
| `subscriber_id` | Yes |
| `tower_id` | Yes |
| `opened_time` | Yes |
| `closed_time` | No |
| `ticket_type` | Yes |
| `priority` | Yes |
| `status` | Yes |
| `description` | No |
| `region` | Yes |

## outages

Path: `data/raw/operations/outages.csv`  
Primary key: `outage_id`

| Column | Required |
|---|---|
| `outage_id` | Yes |
| `tower_id` | Yes |
| `outage_start` | Yes |
| `outage_end` | Yes |
| `outage_type` | Yes |
| `root_cause` | Yes |
| `affected_subscribers` | Yes |
| `region` | Yes |

