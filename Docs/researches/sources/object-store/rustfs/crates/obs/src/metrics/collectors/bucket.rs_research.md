<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket.rs

## Purpose
Adapts per-bucket usage and quota statistics into Prometheus metrics using the node-bucket metric descriptors.

## Important APIs, Types, and Functions
`BucketStats` carries bucket `name`, `size_bytes`, `objects_count`, and `quota_bytes`. `collect_bucket_metrics` emits three metrics per bucket: usage bytes, objects total, and quota bytes, each labeled by `bucket`.

## Control Flow
Empty input returns an empty vector. Non-empty input preallocates `buckets.len() * 3`, clones each bucket name into a `Cow`, and pushes descriptor-backed `PrometheusMetric` values. Zero quota is still emitted as a metric value.

## State and Persistence
Stateless snapshot conversion. It does not query storage directly or persist previous values.

## Dependencies and Integration
Uses `PrometheusMetric`, `report_metrics` in tests, and descriptors from `crate::metrics::schema::node_bucket`. HTTP metrics handlers or background collectors should populate `BucketStats` from storage/admin sources.

## Risks
Bucket names are metric labels, so very large bucket counts increase cardinality. Values are converted from `u64` to `f64`, which can lose exact precision above 2^53. The collector trusts callers to provide consistent quota semantics.

## Test Signals
Tests verify metric count and labels for multiple buckets, quota reporting, empty input, explicit zero-quota output, and `BucketStats::default` values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/bucket.rs -->
