# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_counter.go

Purpose: implements a `SnapshotValueAggregator` for counter time series.

Important APIs/types/functions: `CounterValue`, `TimeseriesAggregator`, `FromSnapshot`, and `Aggregate`.

Control flow: `CounterValue` returns an aggregator bound to one counter name. `FromSnapshot` reads that counter from a snapshot map and reports whether it exists. `Aggregate` adds a ratio-scaled incoming value to the existing aggregate, truncating to `int64`.

State/persistence behavior: no internal state beyond the metric name. It reads snapshot counter maps and writes aggregate values in `CreateTimeSeries`.

Dependencies/integration: used by `metrics_timeseries.go` tests and callers that need counter history by time period.

Risks/test signals: fractional scaling truncates, so totals can lose small values when snapshots are split across many periods. Missing counters are skipped entirely.
