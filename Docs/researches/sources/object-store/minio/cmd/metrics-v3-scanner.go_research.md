# sources/object-store/minio/cmd/metrics-v3-scanner.go

Purpose: Exposes v3 scanner progress and activity metrics.

Important APIs/types/functions: Defines scanner metrics for bucket scans started/finished, directories scanned, objects scanned, versions scanned, and last activity seconds. `loadClusterScannerMetrics` populates them.

Control flow: The loader reads lifetime counters from `globalScannerMetrics`, treating started scans as completed bucket-drive scans plus active drives. It retrieves cached data usage and sets last activity as seconds since `LastUpdate` if available, logging cache errors.

State and persistence behavior: Stateless over global scanner counters and cached data usage. Last activity reflects data usage update time, which may be zero or stale if scanner data has not been captured.

Dependencies and integration points: Depends on `globalScannerMetrics`, `metricsCache.dataUsageInfo`, and scanner metric constants shared with other MinIO subsystems.

Risks: If `LastUpdate` is zero but cache retrieval succeeds, `time.Since` would produce a very large value; unlike usage loaders, this file does not explicitly skip zero `LastUpdate`. The comment says "cluster webhook", which is stale and could confuse maintainers.

Test signals: No direct tests in this subset.
