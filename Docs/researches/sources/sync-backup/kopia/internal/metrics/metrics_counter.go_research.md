# sources/sync-backup/kopia/internal/metrics/metrics_counter.go

Purpose: implements monotonic integer counters backed by both an atomic in-memory state and a Prometheus counter.

Important APIs/types/functions: `Counter`, `Add`, `Snapshot`, `newState`, and `Registry.CounterInt64`.

Control flow: `Add` is nil-safe, increments Prometheus by `float64(v)`, and atomically adds to local state. `Snapshot(false)` loads current state, while `Snapshot(true)` swaps it to zero and returns the previous value. The registry method uses name plus label suffix as a map key and creates a Prometheus counter on first request.

State/persistence behavior: local counter state is in memory and resettable by snapshots; Prometheus counters remain monotonic and are not reset by `Snapshot(true)`. Registry maps retain created counters for the registry lifetime.

Dependencies/integration: depends on Prometheus client helpers defined elsewhere in the metrics package and registry locking in `metrics_registry.go`.

Risks/test signals: Prometheus counters should not receive negative values; this code does not guard against negative `Add`. Label suffix construction is order-sensitive because maps are iterated without sorting.
