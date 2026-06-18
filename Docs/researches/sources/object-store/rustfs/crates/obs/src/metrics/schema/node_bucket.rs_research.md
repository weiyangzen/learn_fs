# sources/object-store/rustfs/crates/obs/src/metrics/schema/node_bucket.rs

## Purpose
Defines simple per-bucket node/API usage descriptors for bucket bytes, object count, and quota.

## Important APIs, Types, and Functions
Exports private `BUCKET_LABEL` and three `LazyLock<MetricDescriptor>` values: `BUCKET_USAGE_BYTES_MD`, `BUCKET_OBJECTS_TOTAL_MD`, and `BUCKET_QUOTA_BYTES_MD`. They use `MetricName::Custom` suffixes and `subsystems::BUCKET_API`, each labeled by `bucket`.

## Control Flow
Lazy descriptor construction only.

## State and Persistence
No values or persistence. Collector data comes from storage bucket lists, backend data usage, and quota config.

## Dependencies and Integration Points
Used by `metrics/collectors/bucket.rs`, which emits per-bucket metrics. It overlaps conceptually with `cluster_usage.rs` per-bucket descriptors but uses different names under the bucket API subsystem.

## Risks
Custom metric names bypass enum-level naming review. Hidden bucket filtering is handled by collectors, not descriptor schema. There is potential dashboard confusion between bucket API usage metrics and cluster usage bucket metrics.

## Test Signals
No schema tests. Bucket collector tests check representative names and labels.
