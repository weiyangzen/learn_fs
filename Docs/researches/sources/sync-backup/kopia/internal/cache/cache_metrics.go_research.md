## sources/sync-backup/kopia/internal/cache/cache_metrics.go

Purpose: defines metrics counters for content cache hits, misses, malformed data, and errors.

Important APIs/types/functions: `metricsStruct`, `initMetricsStruct`, and report helpers for miss errors, miss bytes, hit bytes, malformed data, and store errors.

Control flow, state, and persistence: initializes counters in a registry with a `cache` label. Report helpers increment counts/bytes; metric values persist only in the metrics registry.

Dependencies and integration points: used by persistent/content cache internals to expose operational visibility.

Risks and test signals: typo-level risk in metric descriptions, and nil registry handling depends on `metrics.Registry` behavior. No direct tests in this subset.
