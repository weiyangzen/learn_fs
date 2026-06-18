# sources/storage-engines/foundationdb/contrib/observability_splunk_dashboard/performance_overview.xml

## Purpose
This Splunk Simple XML dashboard provides a high-level FoundationDB performance overview. It charts transaction/read/write rates, latency percentiles, ratekeeper throttling, disk overhead, KV/disk size, roles, storage engine, and recovery generations.

## Important APIs, Types, And Functions
The form label is `FoundationDB - Performance Overview (Dev WiP)`. Inputs define `Index`, `LogGroup`, `TimeSpan`, `UpdateRateTypeToken` for normal vs batch ratekeeper updates, and `ChartBinSizeToken` for binning. Panels query `ProxyMetrics`, `GrvProxyMetrics`, `StorageMetrics`, `GRVLatencyMetrics`, `CommitLatencyMetrics`, `ReadLatencyMetrics`, `RkUpdate*`, `DDTrackerStats`, `ProcessMetrics`, `Role`, and `TLogMetrics`.

## Control Flow
With `autoRun=true`, panels execute when the dashboard loads and token changes trigger refreshes. Searches use `bin _time span=$ChartBinSizeToken$`, `stats`, `timechart`, `eval`, `foreach`, and `table` to aggregate rates and sizes. Ratekeeper panels select event type dynamically with `RkUpdate$UpdateRateTypeToken$`; disk overhead combines storage metrics with DD tracker logical size; role/storage-engine panels summarize recent process/role events.

## State And Persistence Behavior
The XML is static dashboard state only. It does not write to Splunk indexes or FDB. User-selected tokens determine runtime search state.

## Dependencies And Integration Points
It depends on Splunk Simple XML, FDB trace logs with expected metric fields, and consistent `TrackLatestType="Original"` event semantics. It complements the detailed and histogram dashboards by giving first-screen cluster health/performance signals.

## Risks And Edge Cases
`autoRun=true` can trigger many searches immediately, which is expensive for large indexes. Tokenized event type construction for ratekeeper searches can fail silently if values do not match available event types. Some queries aggregate across all hosts/machines and may hide skew. The dashboard is marked Dev WiP, so panel definitions may not be production-hardened. Log-scale or capped axes can hide zero/missing data and extreme values.

## Test Signals
Validation should confirm XML imports cleanly, all token defaults produce valid searches, charts populate on representative trace data, normal/batch ratekeeper selection works, bin-size token changes affect aggregation, and high-cardinality log groups do not exceed Splunk search limits.
