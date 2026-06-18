# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_usage.rs

## Purpose
Defines metric descriptors for cluster-wide object usage and per-bucket usage. It covers byte totals, object/version/delete-marker counts, bucket counts, quotas, and distribution buckets.

## Important APIs, Types, and Functions
Exports label constants `BUCKET_LABEL` and `RANGE_LABEL`, plus `LazyLock<MetricDescriptor>` descriptors for cluster object metrics under `CLUSTER_USAGE_OBJECTS` and bucket metrics under `CLUSTER_USAGE_BUCKETS`. Distribution metrics declare `range`; per-bucket metrics declare `bucket`; per-bucket distributions declare both `range` and `bucket`.

## Control Flow
Each descriptor is lazily constructed with `new_gauge_md`. There is no behavior besides descriptor metadata creation.

## State and Persistence
No values are stored here. Values are derived in `collect_cluster_usage_metric_stats()` from persisted backend data-usage snapshots loaded through `load_data_usage_from_backend()`, plus per-bucket quota config lookups.

## Dependencies and Integration Points
Used by `metrics/collectors/cluster_usage.rs`, which converts `ClusterUsageStats` and `BucketUsageStats` into Prometheus metrics and applies labels matching these descriptors. Integrated with `MetricName` mappings such as `UsageTotalBytes`, `UsageBucketObjectSizeDistribution`, and `UsageVersionCountDistribution`.

## Risks
Distribution labels must be ordered consistently with collector label insertion. Hidden buckets beginning with `.` are filtered by the collector, not by this schema. Usage data is snapshot-based, so metrics can lag actual object changes. A stale or missing backend usage file causes the collector to return no usage metrics.

## Test Signals
No direct tests in the schema. Collector-level tests check representative full names. Stronger coverage would assert descriptor label sets and all expected distribution labels.
