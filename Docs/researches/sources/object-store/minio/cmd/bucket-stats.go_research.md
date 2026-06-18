# sources/object-store/minio/cmd/bucket-stats.go

## Purpose
This file defines bucket-level replication statistics, queue summaries, transfer-rate summaries, and rolling replication latency/count windows. These structures back MinIO's replication monitoring and admin responses, and they are serialized by generated msgp code.

## Important APIs, types, and functions
`ReplicationLatency` wraps `LastMinuteHistogram` and exposes `merge`, `getUploadLatency`, and `update`. `ReplicationLastMinute` and `ReplicationLastHour` track rolling counters with `addsize`, `getTotal`, `merge`, and `forwardTo`. `BucketStatsMap` maps bucket names to `BucketStats`; `BucketStats` combines uptime, replication stats, queue stats, and proxy stats. `BucketReplicationStats` is the bucket aggregate with per-target stats and compatibility fields. `BucketReplicationStat` is the per-target record for replicated/replica size, failure metrics, latency, bandwidth, transfer rates, and deprecated pending/failed counters. `ReplQNodeStats` and `ReplicationQueueStats` package node queue and worker summaries.

## Control flow
Rolling metrics update incrementally. `ReplicationLastHour.addsize` advances a 60-slot ring by minute and clears stale slots through `forwardTo`; `getTotal` advances before summing. `ReplicationLatency.update` adds latency into a size-class histogram. `BucketReplicationStats.Clone` copies scalar fields, recreates the per-target map, and clones transfer trackers. `ReplicationStats.getNodeQueueStats` reads qCache and the stats cache under lock, builds per-target large/small/total transfer summaries, then derives node totals. `getNodeQueueStatsSummary` merges transfer stats across all buckets for site-level totals.

## State and persistence behavior
The file defines mutable data held by `ReplicationStats.Cache`, qCache, and MRF counters elsewhere. Exported fields and JSON/msgp tags are admin API and binary compatibility contracts. Deprecated fields remain serialized for older consumers.

## Dependencies and integration points
Dependencies include `madmin` timed error stats, active worker/queue/MRF structures, `XferStats`, `RTimedMetrics`, `InQueueMetric`, `ProxyMetric`, `LastMinuteHistogram`, `lastMinuteLatency`, and globals such as `globalLocalNodeName`, `globalBootTime`, and `globalReplicationStats`. The `//go:generate msgp -file $GOFILE` directive ties this source to `bucket-stats_gen.go` and its tests.

## Risks and test signals
Schema compatibility is the main risk. Window logic must clear stale slots after idle periods, and consumers must tolerate missing transfer entries when no traffic exists. `BucketReplicationStats.Clone` deserves review for possible `Failed.ErrCounts` aliasing. Generated msgp tests cover serialization mechanics, but this subset has no focused tests for rolling-window math, aggregation, clone isolation, or JSON compatibility.
