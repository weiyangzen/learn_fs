# sources/sync-backup/kopia/internal/metrics/metrics_throughput_test.go

Purpose: validates nil-safe throughput observations and Prometheus export of backing byte and duration counters.

Important APIs/types/functions: `metrics.NewRegistry`, `Registry.Throughput`, `Throughput.Observe`, and `mustFindMetric`.

Control flow: nil test obtains throughput from a nil registry and calls `Observe`. Non-nil test creates a throughput metric, checks both Prometheus counters start at zero, records two observations, and verifies total bytes and total nanoseconds.

State/persistence behavior: uses in-memory registry state plus process-global Prometheus counters. No snapshot reset is tested.

Dependencies/integration: uses Prometheus client model and `testify/require`.

Risks/test signals: tests confirm counter naming suffixes but do not cover labels, snapshot content, or concurrent throughput creation.
