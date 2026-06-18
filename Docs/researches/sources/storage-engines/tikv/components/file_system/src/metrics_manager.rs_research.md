<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/metrics_manager.rs -->
# sources/storage-engines/tikv/components/file_system/src/metrics_manager.rs

Purpose: this module turns either rate-limiter counters or OS I/O stats collector values into Prometheus byte counter deltas.

Important APIs and types: `BytesFetcher` has two modes: `FromRateLimiter(Arc<IoRateLimiterStatistics>)`, which reads atomic counters from the limiter, and `FromIoStatsCollector()`, which calls `fetch_io_bytes`. `MetricsManager` stores a fetcher and `last_fetch` array of `IoBytes`.

Control flow: `MetricsManager::flush` first flushes TLS histogram metrics, fetches the latest byte totals, iterates every `IoType`, computes `latest - last_fetch` using saturating subtraction, increments `IO_BYTES_VEC` read/write counters by the delta, and updates `last_fetch`.

State and persistence behavior: manager state is in-memory only. Prometheus counters are process-global and monotonic. `last_fetch` prevents double-counting totals across flushes.

Dependencies and integration points: it depends on `strum::IntoEnumIterator` over `IoType`, `IoRateLimiterStatistics`, `io_stats::fetch_io_bytes`, and `metrics::IO_BYTES_VEC`. TiKV can choose whether metrics come from limiter-observed bytes or OS-observed disk bytes.

Risks: using rate-limiter stats records logical permitted bytes, not necessarily durable disk bytes, while OS collectors record kernel/accounted bytes; switching fetcher modes changes metric meaning. Saturating delta hides counter resets or collector failures as zero rather than negative deltas.

Test signals: no local tests exist. Behavior is small and indirectly covered by limiter statistics and I/O stats tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/metrics_manager.rs -->
