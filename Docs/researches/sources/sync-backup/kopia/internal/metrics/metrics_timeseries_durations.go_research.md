# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_durations.go

Purpose: implements a snapshot aggregator for duration distribution time series.

Important APIs/types/functions: `DurationDistributionValue`, `DurationDistributionValueAggregator`, `FromSnapshot`, `Aggregate`, and the compile-time `SnapshotValueAggregator` assertion.

Control flow: `FromSnapshot` selects a named duration distribution from a snapshot. `Aggregate` initializes an empty `DistributionState` if needed, then merges the incoming distribution with bucket counters scaled by the time-overlap ratio.

State/persistence behavior: aggregation mutates and returns the accumulated distribution state for a time bucket. It carries count/sum/min/max from incoming states without scaling count or sum, while bucket counters are scaled.

Dependencies/integration: works with generic distribution merge logic and `CreateTimeSeries`.

Risks/test signals: `mergeScaledFrom` scales buckets but not `Count` or `Sum`, so time-sliced distribution time series may have bucket counts proportionally split while count/sum remain fully accumulated. This may be intentional but is a semantic hotspot.
