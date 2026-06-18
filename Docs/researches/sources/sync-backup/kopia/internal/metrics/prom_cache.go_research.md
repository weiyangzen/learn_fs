# sources/sync-backup/kopia/internal/metrics/prom_cache.go

Purpose: caches Prometheus counter and histogram vectors by metric name so repeated metric observations reuse registered collectors.

Important APIs/types/functions: `getPrometheusCounter`, `getPrometheusHistogram`, generic helpers `mapKeys` and `mapValues`, package globals `promCounters`, `promHistograms`, `promCacheMutex`, and constants for Kopia metric naming.

Control flow: each getter locks the global cache, looks up a `CounterVec` or `HistogramVec` by `opts.Name`, lazily registers it via `promauto`, stores it, and returns a child collector with label values derived from the provided map.

State and persistence behavior: process-global in-memory collector caches persist for the lifetime of the process and are synchronized by a mutex.

Dependencies and integration points: integrates with `prometheus/client_golang`, Go `maps` and `slices`, and the rest of Kopia metrics emission.

Risks and test signals: map key/value iteration is not explicitly sorted, so label names and values can become mismatched if iteration orders differ. Tests should exercise multiple labels, repeated names, and concurrent metric creation.
