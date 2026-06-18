# sources/object-store/minio/cmd/metrics-v3-system-drive.go

Purpose: Exposes v3 node drive metrics for capacity, inode counts, health, API error/latency counters, drive counts, and iostat-derived throughput/latency/utilization.

Important APIs/types/functions: Defines drive label constants `drive`, `pool_index`, `set_index`, `drive_index`, and `api`; drive health values offline/online/healing; capacity/error/latency/count/iostat descriptors; `getCurrentDriveIOStats`; `MetricValues.setDriveBasicMetrics`, `setDriveAPIMetrics`, `setDriveIOStatMetrics`; and `loadDriveMetrics`.

Control flow: `getCurrentDriveIOStats` collects local disk metrics for the local node and maps disk path to I/O stats. `loadDriveMetrics` retrieves cached `storageMetrics`, iterates disks, builds stable labels including pool/set/drive indexes, emits basic capacity/inode/health values, emits cached iostat rate values if available, emits API error and last-minute latency values, then sets aggregate offline/online/total drive counts.

State and persistence behavior: Loader is stateless, but iostat values depend on state maintained in `newDriveMetricsCache`: previous disk counters and refresh time. Health is encoded as 0 offline, 1 online, 2 healing.

Dependencies and integration points: Depends on madmin disk metrics, object-layer local storage info through the cache, drive metrics in `madmin.Disk`, and v3 metrics framework. It is the detailed node-level counterpart to cluster health drive counts.

Risks: First scrape after startup lacks iostat rates. Disk path labels can be high-cardinality or expose host path details. I/O errors are computed as availability minus timeout errors; unexpected counter semantics could produce negative values. The help text includes "microseconds" but the metric name uses `micros`, so consumers should not infer seconds.

Test signals: No direct tests in this subset.
