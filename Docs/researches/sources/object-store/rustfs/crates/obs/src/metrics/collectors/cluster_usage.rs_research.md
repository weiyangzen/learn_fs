# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_usage.rs

Purpose: converts cluster-wide and per-bucket usage statistics into Prometheus metrics for bytes, object counts, version counts, delete markers, quotas, and distribution buckets.

Important APIs/types: `ClusterUsageStats` holds aggregate totals plus object-size and version-count distributions. `BucketUsageStats` adds `bucket`, quota, and per-bucket distributions. Exported collectors are `collect_cluster_usage_metrics` and `collect_bucket_usage_metrics`.

Control flow: cluster collection preallocates base four metrics plus distribution lengths, emits total bytes/objects/versions/delete markers, then emits distribution samples labeled by `range`. Bucket collection iterates buckets, emits five bucket-labeled base metrics, then emits object size and version count distribution metrics labeled by `range` and `bucket`.

State/persistence: stateless conversion; persistent usage data and scan snapshots are read in upstream collectors.

Dependencies/integration: depends on `schema::cluster_usage` descriptors and label constants. Used by the supplementary cluster task when `collect_cluster_usage_metric_stats().await` returns a `(cluster_usage, bucket_usage)` pair.

Risks: bucket-level metrics scale by bucket count times distribution buckets. `quota_bytes = 0` is documented as no quota but still emitted, so dashboards must treat zero carefully. Distribution `range` strings are caller-provided and should be normalized to avoid cardinality/label drift.

Test signals: tests assert cluster output count of 11 for four object-size and three version ranges, descriptor presence for total bytes, and bucket output count of seven for one bucket with one distribution bucket each.
