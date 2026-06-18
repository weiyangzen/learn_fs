# sources/object-store/minio/cmd/metrics-v3-cache.go

Purpose: Provides shared v3 metrics caches for expensive or cross-subsystem data used by metrics loaders.

Important APIs/types/functions: `metricsCache` groups caches for data usage, erasure-set health, local drive metrics, memory metrics, CPU metrics, cluster drive metrics, and node online/offline counts. `newMetricsCache` constructs them. `storageMetrics` carries `madmin.StorageInfo`, iostat-derived metrics, and drive counts. `getDiffStats` and `getDriveIOStatMetrics` derive per-second disk I/O rates from sampled `madmin.DiskIOStats`.

Control flow: Each `new*Cache` returns a `cachevalue.NewFromFunc` with a one-minute TTL and `ReturnLastGood`. Data usage and health call object-layer methods if initialized. CPU and memory call `collectLocalMetrics` for the local node. Drive metrics sample `LocalStorageInfo`, compute drive counts, sample current disk I/O stats, compare with the previous sample under a mutex, store rate metrics when enough time elapsed, then update the previous sample.

State and persistence behavior: No durable persistence. Runtime state includes previous drive I/O samples and refresh timestamps captured by the drive cache closure, plus cached last-good values across all caches. First drive scrape lacks rate metrics because there is no prior sample.

Dependencies and integration points: Integrates with object layer, madmin realtime metrics, cachevalue, health APIs, storage info helpers, and global node identity. It is injected into v3 `MetricsGroup` loaders by the v3 collection setup.

Risks: Caches intentionally hide transient failures by returning last good data, which improves scrape stability but can make stale metrics look fresh. Some loaders ignore cache errors. Drive I/O rate math assumes monotonic disk counters and positive sample duration. `GlobalContext` is used inside cache loaders even when a scrape context is supplied.

Test signals: No direct tests in this subset.
