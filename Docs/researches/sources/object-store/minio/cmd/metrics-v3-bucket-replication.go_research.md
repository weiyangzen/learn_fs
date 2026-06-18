# sources/object-store/minio/cmd/metrics-v3-bucket-replication.go

Purpose: Exposes v3 bucket-level replication metrics for failed bytes/counts, proxied replication target requests, sent bytes/counts, and upload latency distributions.

Important APIs/types/functions: Defines descriptor constants for last-hour, last-minute, total failed, sent, proxied get/head/tagging, delete tagging, latency, and labels `bucket`, `operation`, and `targetArn`. `loadBucketReplicationMetrics` is a `BucketMetricsLoaderFn`. It uses `SetHistogramValues` for latency buckets.

Control flow: The loader returns immediately when site replication is enabled because bucket replication stats are not applicable in that mode. It gets data usage from `metricsCache`, builds latest bucket replication stats with `globalReplicationStats.Load().getAllLatest`, then iterates only requested buckets. For each target ARN with replication usage it sets failure windows, proxy counters, sent counters, total failures, and upload latency histogram values.

State and persistence behavior: It is stateless but depends on cached data usage and live replication stats. Bucket output is constrained by the v3 handler's requested bucket list. Metrics represent a mix of process lifetime counters and recent window gauges.

Dependencies and integration points: Depends on `metricsCache.dataUsageInfo`, `globalSiteReplicationSys`, `globalReplicationStats`, `BucketReplicationStats`, and v3 bucket metric group handling. It complements cluster replication metrics in `metrics-v3-replication.go`.

Risks: `globalReplicationStats.Load()` is used without an explicit nil check in this file, so loader safety depends on replication stats being initialized before this metric group is active. Site replication mode suppresses these metrics entirely. Label `targetArn` can produce high cardinality when many replication targets exist.

Test signals: No direct tests in this subset.
