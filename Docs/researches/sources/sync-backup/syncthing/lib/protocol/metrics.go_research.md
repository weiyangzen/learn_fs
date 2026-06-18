## sources/sync-backup/syncthing/lib/protocol/metrics.go

Purpose: declares protocol metrics for Prometheus or Syncthing's metrics subsystem.

Important content: metric definitions/counters/gauges for protocol traffic or connection behavior, registered at package init or exposed as package variables.

Control flow and state: metric variables are initialized once and updated by protocol connection/counting paths.

Dependencies and integration points: integrates protocol byte counters and connection stats with observability.

Risks: metric label cardinality and registration names must stay stable. Duplicate registration can panic if initialization patterns change.

Test signals: no direct tests in this subset.
