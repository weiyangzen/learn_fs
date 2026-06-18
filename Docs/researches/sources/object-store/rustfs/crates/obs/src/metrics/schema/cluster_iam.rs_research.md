# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_iam.rs

## Purpose
Defines the metric descriptors for cluster IAM synchronization and plugin authentication metrics. The file is schema-only: it names the IAM Prometheus metrics, their metric type, help text, label set, namespace, and subsystem.

## Important APIs, Types, and Functions
Exports ten `pub static LazyLock<MetricDescriptor>` values: `LAST_SYNC_DURATION_MILLIS_MD`, seven plugin authn service metrics, `SINCE_LAST_SYNC_MILLIS_MD`, `SYNC_FAILURES_MD`, and `SYNC_SUCCESSES_MD`. Every descriptor is built with `new_counter_md`, `MetricName::*`, and `subsystems::CLUSTER_IAM`, with no variable labels.

## Control Flow
Each descriptor is lazily initialized on first use. Initialization calls the shared descriptor factory, which binds the RustFS namespace, counter type, IAM subsystem, and static help text. There is no runtime branching after lazy initialization.

## State and Persistence
The file owns no metric values and persists nothing. State exists only as lazily initialized descriptor metadata. Runtime values come from `collect_iam_stats()` in `stats_collector.rs`, which reads global IAM sync and OIDC plugin authn snapshots.

## Dependencies and Integration Points
Depends on `MetricDescriptor`, `MetricName`, `new_counter_md`, and `subsystems`. The collector side imports these descriptors in `metrics/collectors/cluster_iam.rs` and converts sampled `IamStats` fields into `PrometheusMetric` values with matching names.

## Risks
Several metrics with time-like names are counters even though they represent durations or "seconds since" values, which may confuse Prometheus consumers. Because no labels are declared, collector code must not attach dimensions. Any mismatch between `MetricName::as_str()` and dashboard expectations changes exported metric names.

## Test Signals
There are no direct tests in this file. Indirect coverage exists through descriptor factory tests and collector tests that call `get_full_metric_name()`. Useful additional tests would assert all IAM descriptor names and types against expected Prometheus names.
