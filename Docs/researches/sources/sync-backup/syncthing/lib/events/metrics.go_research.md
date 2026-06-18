## sources/sync-backup/syncthing/lib/events/metrics.go

Purpose: Defines Prometheus counters for event creation, delivery, and drops.

Important APIs/types/functions: `metricEvents` is a `CounterVec` under namespace `syncthing`, subsystem `events`, name `total`, labelled by event type and state. State constants are `created`, `delivered`, and `dropped`.

Control flow: Counter is registered at package init. `events.go` increments created when processing logged events, delivered when sent to a subscriber, and dropped on subscriber timeout.

State and persistence: Process metrics only.

Dependencies and integration points: Depends on Prometheus client and event logger delivery path.

Risks: High-cardinality risk is low because event type/state are bounded. Metrics can reveal dropped event pressure but are only accurate if logger service is running.

Test signals: Event tests exercise increments indirectly, but metrics values are not asserted.
