# sources/object-store/minio/cmd/site-replication-metrics.go

## Purpose
Defines in-memory site-replication metric models and update/aggregation logic. It tracks replication counts, bytes, failures, latency, transfer-rate summaries, endpoint health, and summary DTOs exposed through admin/status APIs.

## Important APIs, Types, And Functions
`RStat` stores count and byte totals. `RTimedMetrics` combines last-minute, last-hour, since-uptime, and error-code counts; methods `String()`, `toMetric()`, `addsize()`, and `merge()` convert, update, and combine timed failure metrics. `SRStats` is the site-level mutable store with replica totals, deployment status map, ticker, and lock. `SRStatus` stores per-deployment replicated size/count, failures, latency, large/small transfer stats, and endpoint identity.

`SRStats.update()` applies `replStat` events, creating per-deployment status as needed and updating completed vs failed metrics. `SRStats.get()` snapshots per-deployment metrics and enriches them with endpoint health from `globalBucketTargetSys.healthStats()`. `SRStatus.updateXferRate()` classifies transfers by `minLargeObjSize`. `newSRStats()`, `trackEWMA()`, and `updateMovingAvg()` maintain EWMA transfer-rate measurements. `SRMetric` and `SRMetricsSummary` are admin-facing metric summaries.

## Control Flow
Replication events enter through `SRStats.update()`, which locks the map and updates counters based on `Completed`, `Failed`, or `Pending`. Readout flows through `get()`, which clones transfer stats, merges large and small transfer rates into totals, translates failure data to `madmin.TimedErrStats`, and overlays endpoint uptime/latency/online status. A background ticker periodically updates moving averages until `GlobalContext` is canceled.

## State And Persistence
State is in memory only in this file. Counters use a mix of mutex-protected map state and atomics inside timed metrics. The EWMA ticker is process-local. Generated msgp code can serialize these types, but this hand-written file does not perform disk writes itself.

## Dependencies And Integration Points
Depends on `madmin-go` admin DTOs, MinIO client error response translation, global bucket target health stats, replication latency/time-window types, queue/proxy/worker metric types, and transfer-stat helpers. It integrates with replication event reporting and admin site-replication metrics responses.

## Risks And Edge Cases
Concurrency correctness depends on callers using `SRStats` methods rather than mutating maps directly. `RTimedMetrics.addsize()` updates atomic totals but also mutates `ErrCounts` without an internal lock; current callers update it under `SRStats.lock`, so that locking contract matters. The generated codec omits some runtime-only fields by tag or structure, so serialization must not be assumed to preserve ticker/lock semantics.

## Test Signals
The generated codec test file covers msgp round trips for `RStat`, `RTimedMetrics`, `SRMetric`, `SRMetricsSummary`, `SRStats`, and `SRStatus`. There is no focused hand-written test here for update aggregation, EWMA behavior, endpoint health enrichment, or AccessDenied error counting.
