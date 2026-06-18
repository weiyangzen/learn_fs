# sources/object-store/rustfs/crates/notify/src/status_view.rs

## Purpose
Provides aggregate status and metric snapshots for the notification system.

## Important APIs, types, and functions
- `NotifyStatusView` wraps `Arc<NotificationMetrics>`.
- `get_status` returns a string map with uptime, processing, processed, failed, and skipped event counts.
- `snapshot_metrics` returns the typed `NotificationMetricSnapshot`.

## Control flow
Methods read atomic counters from `NotificationMetrics` and format them for status callers or Prometheus collection paths.

## State and persistence behavior
No owned mutable state beyond the shared metrics reference. Metrics are in-memory process counters.

## Dependencies and integration points
Used by `NotificationSystem::get_status`, `snapshot_metrics`, and `Drop` logging/metrics emission. Depends on `hashbrown::HashMap` and `NotificationMetrics`.

## Risks and edge cases
The status map values are strings, so typed consumers should prefer `snapshot_metrics`. Uptime changes continuously, making exact tests inappropriate.

## Test signals
Tests verify an empty metrics snapshot has zero counters and that the status map exposes all expected keys.
