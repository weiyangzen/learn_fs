# sources/sync-backup/kopia/internal/metrics/metrics_counter_test.go

Purpose: validates nil-safe counters, unlabeled counters, labeled counters, snapshots, reset behavior, and Prometheus counter export.

Important APIs/types/functions: `metrics.NewRegistry`, `Registry.CounterInt64`, `Counter.Add`, `Counter.Snapshot`, and `mustFindMetric`.

Control flow: nil-registry test verifies calls on nil counters are no-ops. Unlabeled test creates a counter, observes Prometheus value at zero, adds values, checks Prometheus and snapshot totals, then resets local state. Labeled test creates two label variants and verifies independent Prometheus series and totals.

State/persistence behavior: uses process-global Prometheus registry and per-registry in-memory state. Snapshot reset does not reset Prometheus, and the tests only assert local reset after checking Prometheus totals.

Dependencies/integration: uses Prometheus client model types and `testify/require`.

Risks/test signals: global metric names in tests must remain unique to avoid duplicate registration conflicts. Negative counter behavior is not covered.
