# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_sizes.go

Purpose: implements a snapshot aggregator for size distribution time series.

Important APIs/types/functions: `SizeDistributionValue`, `SizeDistributionValueAggregator`, `FromSnapshot`, `Aggregate`, and the compile-time `SnapshotValueAggregator` assertion.

Control flow: the aggregator extracts a named size distribution from a snapshot and merges it into a per-time-bucket accumulated `DistributionState[int64]`, scaling bucket counters according to snapshot overlap ratio.

State/persistence behavior: no standalone state beyond the metric name; aggregation mutates bucket-level accumulated distribution states in the time-series builder.

Dependencies/integration: mirrors duration distribution aggregation and uses generic distribution merge behavior.

Risks/test signals: like duration aggregation, bucket counters are scaled but count and sum are not scaled, creating possible interpretation differences for partially overlapping snapshots. Missing distribution names skip snapshots.
