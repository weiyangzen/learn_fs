# sources/object-store/minio/cmd/metrics-resource.go

Purpose: This file implements MinIO's resource metrics collector for Prometheus: periodic local resource sampling, rolling current/average/max values, peer collection, and handler construction for `/v2/metrics/resource`.

Important APIs and types: Constants define collection/cache intervals and resource metric names for drives, network interfaces, memory, and CPU. `PeerResourceMetrics`, `ResourceMetrics`, and `ResourceMetric` model collected values. Key functions are `getResourceKey`, `updateResourceMetrics`, `updateDriveIOStats`, `collectDriveMetrics`, `collectLocalResourceMetrics`, `initLatestValues`, `startResourceMetricsCollection`, `prepareResourceMetrics`, `getResourceMetrics`, and `metricsResourceHandler`. `minioResourceCollector` implements Prometheus `Describe` and `Collect`.

Control flow: `init` builds help text, registers the resource metrics group, and creates the collector. `startResourceMetricsCollection` initializes disk baselines, clears the global map, samples once, then samples every minute until `GlobalContext` is done. Sampling calls `collectLocalMetrics` for disk/net/mem/CPU, converts cumulative network counters into deltas, records memory totals and percentages, computes CPU percentage/load values, updates drive IO rates from disk stat deltas, and records drive space/inode gauges. Prometheus collection publishes local cached metrics and remote peer metrics concurrently.

State and persistence behavior: Runtime state is held in `resourceMetricsMap`, protected by `resourceMetricsMapMu`, and drive baselines in `latestDriveStats`, protected by `latestDriveStatsMu`. `ResourceMetric` tracks current, cumulative baseline, max, sum, average, and count. There is no on-disk persistence.

Dependencies and integration points: It depends on `collectLocalMetrics`, `globalNotificationSys.GetResourceMetrics`, Prometheus client APIs, MinIO `MetricsGroupV2`, metric description helpers, local drive maps, and madmin disk IO structures. It feeds the resource metrics HTTP handler registered by `metrics-router.go`.

Risks: `getResourceKey` concatenates map values in iteration order; current callers mostly use zero or one label, but multi-label metrics could become nondeterministic. `updateResourceMetrics` compares `metric.Current` but assigns `metric.Max = val`, which is subtle for cumulative counters. CPU percentage calculation assumes non-zero total time. The collector publishes peer and local metrics concurrently, so slow peers can affect scrape latency.

Test signals: No direct tests are present in this subset. Useful signals would include deterministic metric keys, correct cumulative deltas, drive IO rate math across refresh intervals, average/max behavior, no divide-by-zero CPU failures, and Prometheus output containing local and peer resource metrics with expected labels.
