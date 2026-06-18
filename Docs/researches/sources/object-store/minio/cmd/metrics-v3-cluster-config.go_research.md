# sources/object-store/minio/cmd/metrics-v3-cluster-config.go

Purpose: Exposes cluster storage-class parity configuration as v3 metrics.

Important APIs/types/functions: Defines `configRRSParity`, `configStandardParity`, their gauge descriptors, and `loadClusterConfigMetrics`.

Control flow: The loader retrieves cached cluster drive metrics from `c.clusterDriveMetrics`. On success it reads `storageInfo.Backend.StandardSCParity` and `RRSCParity` and sets both gauges. On error it logs with `metricsLogIf` and returns nil to keep collection alive.

State and persistence behavior: Stateless; values come from cached cluster storage info refreshed by `metrics-v3-cache.go`.

Dependencies and integration points: Depends on `metricsCache.clusterDriveMetrics`, storage info backend parity fields, and the v3 metrics group framework. It mirrors some v2 storage class metrics in a smaller v3 module.

Risks: If storage info is stale or unavailable, parity metrics can be stale or absent. There is no explicit object-layer guard here beyond the cache returning zero values when not initialized.

Test signals: No direct tests in this subset.
