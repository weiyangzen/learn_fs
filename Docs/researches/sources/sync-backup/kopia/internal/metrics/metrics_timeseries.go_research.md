# sources/sync-backup/kopia/internal/metrics/metrics_timeseries.go

Purpose: converts metric snapshots into time series by spreading snapshot values proportionally over time buckets and aggregating by user, host, or all snapshots.

Important APIs/types/functions: `TimeSeries`, `TimeSeriesPoint`, `AggregateByFunc`, `AggregateByUser`, `AggregateByHost`, `AggregateAll`, `AggregateMetricsOptions`, `SnapshotValueAggregator`, and `CreateTimeSeries`.

Control flow: `CreateTimeSeries` defaults to user@host aggregation and daily resolution. For each snapshot it extracts a value, computes the first and last time buckets, then walks buckets from `StartTime` to `EndTime`, computing the fraction of snapshot duration in each bucket and delegating scaled aggregation to the value handler. Finally it converts nested maps to sorted point slices.

State/persistence behavior: output is a newly allocated map of sorted time series. Snapshot values are read only. The function assumes non-zero snapshot duration to avoid invalid ratio calculations.

Dependencies/integration: works with counter and distribution aggregators from sibling files and time resolution functions from `metrics_timeseries_timeres.go`.

Risks/test signals: integer aggregators truncate fractional contributions. Zero-length snapshots can divide by zero. `minTime` and `maxTime` are computed but not used in output.
