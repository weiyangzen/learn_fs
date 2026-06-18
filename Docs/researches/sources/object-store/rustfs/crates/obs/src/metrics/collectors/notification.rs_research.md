# sources/object-store/rustfs/crates/obs/src/metrics/collectors/notification.rs

Purpose: converts aggregate notification subsystem counters/gauges into Prometheus metrics for current sends, error events, sent events, and skipped events.

Important APIs/types: `NotificationStats` with four `u64` fields and `collect_notification_metrics(&NotificationStats)`.

Control flow: fixed four-metric vector, no labels, direct mapping to descriptors from `schema::cluster_notification`.

State/persistence: stateless. Runtime notification counters are obtained through `rustfs_notify::notification_metrics_snapshot` in the scheduler.

Dependencies/integration: scheduler notification task builds `NotificationStats` from the snapshot, appends target-specific metrics from `notification_target.rs`, and reports the combined vector.

Risks: aggregate counts are unlabeled, so multiple notification subsystems would need explicit target-level metrics for attribution. Default zero output should not be emitted as a substitute for unavailable notification state unless intentionally desired.

Test signals: tests check four metrics, representative sent/error values, `report_metrics` compatibility, and default zero/no-label behavior.
