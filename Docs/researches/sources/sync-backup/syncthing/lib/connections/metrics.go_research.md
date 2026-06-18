## sources/sync-backup/syncthing/lib/connections/metrics.go

Purpose: Defines the Prometheus gauge for active connections per remote device.

Important APIs/types/functions: `metricDeviceActiveConnections` is a `promauto.NewGaugeVec` under namespace `syncthing`, subsystem `connections`, name `active`, labelled by `device`. `registerDeviceMetrics` pre-creates a label series for a device.

Control flow: Registration is passive at package initialization. Runtime call sites in `service.CommitConfiguration` register new devices and delete removed-device labels; `deviceConnectionTracker.accountAddedConnection` increments and `accountRemovedConnection` decrements.

State and persistence: Metrics live in the process-global Prometheus registry. No durable state is written.

Dependencies and integration points: Depends on `prometheus` and `promauto`. Integrates with connection tracking and config device lifecycle.

Risks: Incorrect add/remove accounting can leave negative or stale gauges. Label cardinality is bounded by configured devices but still depends on config churn.

Test signals: No direct tests in this file; behavior is indirectly exercised by connection tracking tests elsewhere.
