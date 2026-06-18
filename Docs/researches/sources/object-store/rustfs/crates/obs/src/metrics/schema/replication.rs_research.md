# sources/object-store/rustfs/crates/obs/src/metrics/schema/replication.rs

## Purpose
Defines site-level replication worker, queue, transfer-rate, and backlog descriptors.

## Important APIs, Types, and Functions
Exports thirteen gauge descriptors for averages, current values, last-minute queue values, maxima, data transfer rates, and recent backlog count. All use `MetricName::Replication*`, no labels, and `subsystems::REPLICATION`.

## Control Flow
Lazy construction only. Runtime aggregation and conversion are outside this schema.

## State and Persistence
No values are stored. `collect_replication_stats()` reads `GLOBAL_REPLICATION_STATS`, site metrics, bucket bandwidth reports, and bucket target stats to build `ReplicationStats`.

## Dependencies and Integration Points
Used by `metrics/collectors/replication.rs`. It complements bucket-replication schemas outside this subset that expose per-bucket and per-target replication details.

## Risks
All descriptors are gauges, including max values that reset with process lifetime. Missing global replication stats return defaults, so dashboards must distinguish zero from unavailable where possible. Data-transfer-rate aggregation depends on runtime statistics shape.

## Test Signals
Collector tests assert representative full names such as current and average active workers. No schema-local tests.
