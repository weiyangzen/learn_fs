# sources/sync-backup/kopia/internal/metrics/metrics_throughput.go

Purpose: represents throughput as two counters: total bytes/items and total duration in nanoseconds.

Important APIs/types/functions: `Throughput`, `Observe`, and `Registry.Throughput`.

Control flow: `Observe` is nil-safe and adds `size` to the `_bytes` counter and `dt.Nanoseconds()` to the `_duration_nanos` counter. The registry method reuses throughput instances by full name or creates the two backing counters on first use.

State/persistence behavior: state is stored in the two backing counters and participates in registry snapshots and Prometheus export as counters. The `Throughput` wrapper has no independent persisted state.

Dependencies/integration: depends on `CounterInt64` and `labelsSuffix`. Consumers derive rates from the paired counters.

Risks/test signals: `Registry.Throughput` accesses `allThroughput` without locking, unlike counter/distribution constructors, so concurrent creation can race. Negative sizes or durations are not guarded.
