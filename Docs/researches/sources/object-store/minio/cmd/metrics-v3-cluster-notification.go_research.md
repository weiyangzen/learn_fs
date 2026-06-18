# sources/object-store/minio/cmd/metrics-v3-cluster-notification.go

Purpose: Exposes cluster-level notification subsystem metrics for current sends, sent events, failed events, and skipped events.

Important APIs/types/functions: Defines `notificationCurrentSendInProgress`, `notificationEventsErrorsTotal`, `notificationEventsSentTotal`, `notificationEventsSkippedTotal`, descriptors, and `loadClusterNotificationMetrics`.

Control flow: The loader returns nil if `globalEventNotifier` is absent. Otherwise it gets target-list stats and sets four aggregate metrics.

State and persistence behavior: Stateless over notification target-list state. Current send in progress is a live value; total, error, and skipped event values are process-lifetime counters.

Dependencies and integration points: Depends on `globalEventNotifier.targetList.Stats()` and v3 metrics infrastructure. It surfaces cluster notification health separately from per-target logger/audit webhook metrics.

Risks: `notificationCurrentSendInProgressMD` is declared as a counter even though the value is a current in-progress count and should conceptually be a gauge. This type mismatch can affect Prometheus semantics.

Test signals: No direct tests in this subset.
