# sources/sync-backup/kopia/internal/metrics/metrics_distribution.go

Purpose: implements generic numeric distributions for durations and sizes, recording min, max, sum, count, bucket counters, and Prometheus histograms.

Important APIs/types/functions: `realNumber`, `DistributionState[T]`, `mergeFrom`, `mergeScaledFrom`, `Mean`, `Distribution[T]`, `Observe`, `Snapshot`, `newState`, `Registry.DurationDistribution`, and `Registry.SizeDistribution`.

Control flow: `Observe` reads current state pointer, computes the bucket using thresholds, emits a scaled Prometheus observation, then locks and updates sum/count/min/max/bucket count. `Snapshot(false)` copies current state; `Snapshot(true)` swaps in a fresh state with initialized buckets. Registry constructors build Prometheus bucket slices from configured thresholds and reuse distributions by full name.

State/persistence behavior: distribution state is in-memory and resettable for repository metric snapshots; Prometheus histograms are cumulative. `DistributionState` JSON omits thresholds, but thresholds are retained internally for future aggregation.

Dependencies/integration: uses Prometheus histograms, generic constraints, and threshold definitions. Duration values are exported to Prometheus in milliseconds or nanoseconds depending on threshold set.

Risks/test signals: `Observe` loads the state pointer before locking; reset can swap state concurrently, so observations around resets may land in the old state. Label suffix ordering has the same map-order risk as counters. Bucket merges assume compatible bucket lengths.
