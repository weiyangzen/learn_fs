<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/audit.rs -->
# sources/object-store/rustfs/crates/obs/src/metrics/collectors/audit.rs

## Purpose
Adapts audit target statistics into Prometheus metrics using the crate's audit metric descriptors.

## Important APIs, Types, and Functions
`AuditTargetStats` carries `target_id`, `failed_messages`, `queue_length`, and `total_messages`. `collect_audit_metrics` returns three metrics per target: failed messages, queue length, and total messages, each labeled with `target_id`.

## Control Flow
The collector returns an empty vector for empty input. Otherwise it preallocates `stats.len() * 3`, clones the target id into a `Cow<'static, str>`, and pushes metrics created from descriptors with the target label.

## State and Persistence
Stateless. It converts caller-provided snapshots into metric values and does not retain history.

## Dependencies and Integration
Uses `PrometheusMetric` and descriptors from `crate::metrics::schema::audit`. Intended for metrics endpoints or runtime collectors that can assemble audit subsystem stats.

## Risks
Target IDs become metric labels, so high-cardinality target naming can increase Prometheus load. Counts are cast to `f64`, which is standard for Prometheus text metrics but can lose integer precision at very large values.

## Test Signals
Tests cover two-target metric count and label lookup, plus empty input returning no metrics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/metrics/collectors/audit.rs -->
