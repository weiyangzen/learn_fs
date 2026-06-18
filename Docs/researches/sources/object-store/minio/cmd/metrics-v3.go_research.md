# sources/object-store/minio/cmd/metrics-v3.go

This file assembles the v3 metrics catalog. It defines collector paths under `/minio/metrics/v3`, constructs all `MetricsGroup` instances, adds labels and cache objects, registers each group into its own Prometheus sub-registry, and records the sorted path list for routing and discovery.

The exported behavior is centered on `newMetricGroups(r *prometheus.Registry) *metricsV3Collection`. The function builds groups for API requests, bucket API, bucket replication, internode network, drives, memory, CPU, process, cluster health, usage, erasure set health, notification, IAM, replication, config, ILM, scanner, audit, logger webhook, and debug Go collector output. Bucket groups use `NewBucketMetricsGroup` because the bucket list arrives from the request path; non-bucket groups use `NewMetricsGroup`. Non-cluster groups get constant `server` label data through `AddExtraLabels`, currently including `serverName` and `globalLocalNodeName`.

State is runtime registration state: maps from `collectorPath` to groups, a shared `metricsCache`, per-path gatherers, and the sorted collector path list. There is no durable persistence. Integration points include every metric descriptor/loader file in `cmd`, Prometheus `collectors.NewGoCollector`, the outer metrics v3 HTTP route, and global node identity.

Risks: descriptor and loader mismatches panic via `MetricsGroup.validate` or `MetricValues.Set`. Every path is registered into both a sub-registry and the supplied root registry; duplicate registration would be fatal. The group list is a central integration hotspot whenever metrics are renamed or added. Test signal is indirect, from compile-time references to all metric descriptors and any metrics endpoint tests.
