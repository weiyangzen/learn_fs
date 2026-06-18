# sources/object-store/rustfs/crates/ecstore/src/bucket/replication/replication_state.rs

## Purpose
This file owns in-memory replication telemetry for buckets, site replication, queue depth, proxy calls, failures, transfer rates, latency, and active replication workers. It is a metrics/state aggregation layer rather than persistent configuration: callers update counters when replication events happen, background tasks age rolling samples, and read APIs expose bucket/node summaries for monitoring and admin surfaces.

## Important APIs, Types, and Functions
- `ExponentialMovingAverage` stores a floating-point rate in an `AtomicU64` bit pattern plus a `Mutex<SystemTime>` update timestamp. It provides `add_value`, `get_current_average`, `update_exponential_moving_average`, `merge`, `Clone`, `Default`, and custom serde.
- `XferStats` tracks `avg`, `curr`, `peak`, and a moving-average measure. `add_size` converts bytes over duration into bytes/second and splits later into small/large transfer channels.
- `ReplStat` is a transient normalized replication event with ARN, status booleans, operation type, transfer size/duration, endpoint, TLS flag, and optional error.
- `SRStats` is global site-replication size/count via atomics.
- `InQueueStats`, `InQueueMetric`, `QueueCache`, and `QueueSample` track queue byte/count current values and rolling 60-second avg/max snapshots.
- `ProxyMetric` and `ProxyStatsCache` count proxied S3 operations by API and failure state.
- `FailStats`, `FailureSample`, and `FailedMetric` track cumulative failure count/size plus a one-hour recent sample deque.
- `LatencyStats`, `BucketReplicationStat`, `BucketReplicationStats`, `BucketStats`, and `SRMetricsSummary` are the exported report shapes.
- `ActiveWorkerStat` samples active worker counts over a 60-second window.
- `ReplicationStats` is the top-level holder with `Arc<SRStats>`, mutexes for workers/queue/proxy, an async `RwLock` bucket cache, and recent bucket stats.

## Control Flow and State Behavior
`ReplicationStats::start_background_tasks` launches three infinite tokio tasks: every 5 seconds it decays transfer EMAs in the bucket cache, every 2 seconds it samples the global replication pool active worker counts, and every 2 seconds it samples queue counters into rolling queue metrics. The tasks are fire-and-forget and are not cancellable through this API.

`ReplicationStats::update` builds a `ReplStat` from `ReplicatedTargetInfo` only for selected transitions: pending data replication when status changes, completed data replication, failed data replication after pending, and replica object status. Completed and failed updates also feed site-replication stats. Bucket stats are keyed by bucket and replication ARN. Completed events increment replicated size/count and update latency and small/large xfer rate; failed events append to `FailStats`; pending events currently do not mutate additional state.

Queue state is maintained through `inc_q` and `dec_q`. They mutate per-bucket and site-wide `AtomicI64` current bytes/count under the queue-cache mutex. `QueueCache::update` snapshots those atomics into rolling samples. Negative queue counts are possible if decrement calls are unbalanced.

Read paths include `get`, `get_all`, `get_sr_metrics_for_node`, `get_latest_replication_stats`, `get_proxy_stats`, `active_workers`, and `has_replication_usage`. `get_all` merges the main replication cache with queue-only and proxy-only buckets so monitoring can see buckets that only have queue/proxy signals.

## Dependencies and Integration Points
The code integrates with `rustfs_filemeta::{ReplicatedTargetInfo, ReplicationStatusType, ReplicationType}`, the global replication pool via `get_global_replication_pool`, the global bucket bandwidth monitor via `get_global_bucket_monitor`, and crate error types. It uses tokio locks and background intervals for async runtime integration, serde for metrics serialization, and standard atomics for high-frequency counters.

## Persistence
All state is in memory. Serde derives/custom serialization allow report structures to be encoded for API responses or diagnostics, but this file does not write state to disk. Rolling sample deques are skipped by serde in queue/failure/worker structures, so serialized/deserialized metrics lose recent-window history.

## Risks and Edge Cases
- `update_moving_avg_static` mutates only the internal EMA atomics while holding a read lock over the bucket cache. This works because the EMA has interior mutability, but the public `avg` fields in `XferStats` are not refreshed there.
- EMA float updates use relaxed load/store with no compare-and-swap; concurrent writers can lose updates.
- `try_lock`/`try_read` paths silently return stale/default values if locks are contended.
- Background tasks run forever and have no idempotence guard; starting them multiple times duplicates samplers.
- `get_sr_metrics_for_node` uses `UNIX_EPOCH` as boot time, producing process uptime that is really wall-clock seconds since 1970.
- `FailStats::merge` drops recent-window samples, so merged cluster stats cannot answer recent failure windows.
- Queue decrements can underflow below zero logically because atomics use signed integers without floor checks.

## Test Signals
Inline tests cover construction, queue rolling averages, recent failure windows, active worker avg/max, deletion, replica-stat updates, completed replication updates, proxy-only bucket visibility, and `SRStats` initial values. They validate important in-memory behavior but do not exercise background task duplication, bandwidth-monitor integration, lock contention, serialization round trips, or distributed aggregation correctness.
