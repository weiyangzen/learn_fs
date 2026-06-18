# sources/storage-engines/pebble/internal/base/metrics.go

Purpose: Provides small reusable metric accumulators for throughput and sampled gauges.

APIs and types: `ThroughputMetric` with `Merge`, `Subtract`, `PeakRate`, `Rate`, and `Utilization`; `GaugeSampleMetric` with `AddSample`, `Merge`, `Subtract`, and `Mean`.

Control flow and state: `ThroughputMetric` accumulates bytes, work duration, and idle duration. Peak rate divides bytes by work duration, observed rate divides by work plus idle time, and utilization reports the work fraction. `GaugeSampleMetric` stores sample sum and count and derives a mean.

Persistence and dependencies: Runtime-only metrics, not persisted. Depends only on `time`.

Integration points: Used by background workers and metrics collection paths that need cumulative throughput or queue-depth style sampled gauges.

Risks: Rate methods return zero only when bytes are zero; callers should avoid nonsensical nonzero bytes with zero duration. `Subtract` can produce negative durations/counts if misused with unrelated samples.

Test signals: `metrics_test.go` validates merge/subtract/rate/utilization-adjacent behavior for throughput and gauge metrics.
