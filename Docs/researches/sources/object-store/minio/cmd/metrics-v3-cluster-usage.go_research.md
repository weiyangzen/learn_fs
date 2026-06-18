# sources/object-store/minio/cmd/metrics-v3-cluster-usage.go

Purpose: Exposes v3 cluster and bucket usage metrics sourced from MinIO's data usage scan results.

Important APIs/types/functions: Cluster metrics include since-last-update seconds, total bytes, object count, versions count, delete marker count, bucket count, object size distribution, and version count distribution. Bucket metrics include bucket total bytes, objects, versions, delete markers, quota, object size distribution, and object version count distribution. Loaders are `loadClusterUsageObjectMetrics` and `loadClusterUsageBucketMetrics`.

Control flow: Both loaders retrieve `DataUsageInfo` from `c.dataUsageInfo`, log and stop on errors, and return no metrics until `LastUpdate` is non-zero. The cluster loader aggregates usage across all buckets and merges histograms before setting metrics. The bucket loader iterates every usage bucket, retrieves quota from `globalBucketQuotaSys`, emits per-bucket counters/gauges, and emits per-bucket histogram bins.

State and persistence behavior: Stateless over cached data usage, which is derived from backend-scanner persisted usage data. Usage values reflect the last scanner update, not necessarily current object store state. Quota lookup is live per bucket.

Dependencies and integration points: Depends on `metricsCache.dataUsageInfo`, `loadDataUsageFromBackend`, `globalBucketQuotaSys`, and v3 metric descriptors. Scanner metrics also use the same data usage cache for last activity.

Risks: Bucket loader emits all buckets in `DataUsageInfo`, which can be high cardinality compared with v3 bucket-specific API metrics. `usageSinceLastUpdateSeconds` is set with `float64(time.Since(...))` in bucket loader, which represents nanoseconds, while the cluster loader uses `.Seconds()` and the metric name says seconds; this inconsistency is a correctness risk. Quota lookup errors skip the whole bucket's usage metrics.

Test signals: No direct tests in this subset.
