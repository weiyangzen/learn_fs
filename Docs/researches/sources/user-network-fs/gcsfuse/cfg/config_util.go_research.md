## sources/user-network-fs/gcsfuse/cfg/config_util.go

Purpose: Supplies derived default values and small configuration predicates used across gcsfuse.

Important APIs/types/functions: `DefaultFuseMaxPagesLimit`, `DefaultMaxBackground`, `DefaultCongestionThreshold`, `DefaultMaxParallelDownloads`, `IsFileCacheEnabled`, `IsParallelDownloadsEnabled`, `IsTracingEnabled`, `ListCacheTTLSecsToDuration`, `IsMetricsEnabled`, `IsGKEEnvironment`, and `GetBucketType`.

Control flow: defaults derive from page size and CPU count, bounded by `maxBackgroundLimit`. Feature predicates inspect relevant config fields. TTL conversion validates via `isTTLInSecsValid`, maps `-1` to `maxSupportedTTL`, otherwise converts seconds to `time.Duration`. Bucket type priority is zonal, pirlo, hierarchical, flat.

State and persistence: reads process page size at package init into `kernelPageSize`; all functions are otherwise stateless.

Dependencies and integration points: uses runtime CPU count, OS page size, string prefix checks, validation helper from `validate.go`, and `BucketType` from `types.go`.

Risks: invalid TTL causes panic, so callers must validate before conversion. Defaults vary by CPU/page size, which can affect tests or generated defaults across platforms. `IsFileCacheEnabled` treats `MaxSizeMb=-1` as enabled only if `CacheDir` is non-empty.

Test signals: `config_util_test.go` covers default bounds, cache/parallel/tracing/metrics predicates, TTL conversion and panic, GKE mountpoint detection, and bucket priority.
