# sources/object-store/minio/cmd/metrics-v3-cluster-health.go

Purpose: Exposes v3 cluster health rollups for drive counts, node counts, and raw/usable capacity.

Important APIs/types/functions: Defines drive health descriptors (`drives_offline_count`, `drives_online_count`, `drives_count`), node descriptors (`nodes_offline_count`, `nodes_online_count`), and capacity descriptors (`capacity_raw_total_bytes`, `capacity_raw_free_bytes`, `capacity_usable_total_bytes`, `capacity_usable_free_bytes`). Loaders are `loadClusterHealthDriveMetrics`, `loadClusterHealthNodeMetrics`, and `loadClusterHealthCapacityMetrics`.

Control flow: Drive and capacity loaders fetch `c.clusterDriveMetrics`; drive loader emits cached online/offline/total counts, capacity loader computes totals from cached `storageInfo.Disks` with helper functions. Node loader fetches `c.nodesUpDown` and emits peer online/offline counts.

State and persistence behavior: Stateless over the shared metrics cache. Values can be last-good snapshots for up to the cache policy and depend on the notification system and object-layer storage info.

Dependencies and integration points: Depends on `metricsCache.clusterDriveMetrics`, `metricsCache.nodesUpDown`, storage capacity helper functions, and `globalNotificationSys.GetPeerOnlineCount()` through the cache. Complements erasure-set-specific health metrics.

Risks: Cache errors are ignored in these loaders, which favors scrape continuity but can emit zero values if no cached value exists. Capacity helpers depend on correct disk state classification.

Test signals: No direct tests in this subset.
