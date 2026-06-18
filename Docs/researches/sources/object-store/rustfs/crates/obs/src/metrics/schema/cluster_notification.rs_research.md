# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_notification.rs

## Purpose
Provides cluster-level notification metric descriptors for asynchronous event delivery. It distinguishes an in-progress gauge from total sent, skipped, and errored event counters.

## Important APIs, Types, and Functions
Exports four `LazyLock<MetricDescriptor>` values: `NOTIFICATION_CURRENT_SEND_IN_PROGRESS_MD`, `NOTIFICATION_EVENTS_ERRORS_TOTAL_MD`, `NOTIFICATION_EVENTS_SENT_TOTAL_MD`, and `NOTIFICATION_EVENTS_SKIPPED_TOTAL_MD`. The first uses `new_gauge_md`; the others use `new_counter_md`. All use `subsystems::NOTIFICATION` and no labels.

## Control Flow
The file has no active control flow beyond lazy descriptor construction. Descriptor creation follows the shared factories and resolves metric names through `MetricName::Notification*`.

## State and Persistence
No runtime values or persistence are managed here. The actual counters and gauges are supplied by notification collector/runtime stats.

## Dependencies and Integration Points
Depends on the common schema entry layer. `metrics/collectors/notification.rs` imports these descriptors and emits `PrometheusMetric` values from notification stats. The names compose to `rustfs_notification_*`.

## Risks
The file only covers aggregate notification metrics; per-target queue and failure metrics live in `notification_target.rs`. Dashboards must combine both files to get full notification visibility. Naming and label-free descriptors make future per-target expansion a breaking metric shape change if done in place.

## Test Signals
No local tests. The main verification path is collector tests or descriptor snapshot checks for full metric names and metric types.
