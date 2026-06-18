# sources/object-store/minio/cmd/metrics-v3-replication.go

Purpose: Exposes v3 cluster replication queue, worker, transfer-rate, and recent backlog metrics.

Important APIs/types/functions: Defines descriptors for average/current/max active workers, average/current/max data transfer rate, last-minute queued bytes/count, average/max queued bytes/count, and recent backlog count. `loadClusterReplicationMetrics` populates them.

Control flow: The loader loads `globalReplicationStats`; if nil it returns without metrics. It gets a node queue summary, emits queued byte/count gauges for average, max, and current windows, emits active worker gauges, emits transfer rate gauges if transfer stats exist, and emits recent backlog count from MRF stats.

State and persistence behavior: Stateless over replication stats. Values reflect in-memory rolling summaries and process-lifetime or recent-window state maintained by the replication subsystem.

Dependencies and integration points: Depends on `globalReplicationStats.Load()`, queue summary types, and v3 metrics infrastructure. It complements per-bucket replication metrics.

Risks: Transfer rate metrics are omitted when `XferStats` is empty. Metric names differ from v2 in some places, such as `*_data_transfer_rate`, which may require dashboard migration.

Test signals: No direct tests in this subset.
