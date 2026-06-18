<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/metrics.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/metrics.rs

Purpose: `metrics.rs` provides in-memory atomic counters and aggregation helpers for fast-lock performance and health monitoring.

Important APIs/types/functions: `ShardMetrics` owns atomic counters for fast-path success, slow-path success, timeouts, releases, cleanups, contention events, total wait time, and max wait time. It exposes record methods, total acquisition count, fast-path rate, average wait time in nanoseconds, and `snapshot`. `MetricsSnapshot` is an immutable point-in-time copy with helpers for total acquisitions, fast-path rate, average/max wait durations, and timeout rate. `GlobalMetrics` tracks shard count, start time, cleanup runs, and total objects cleaned, and `aggregate_shard_metrics` folds per-shard snapshots into `AggregatedMetrics`. `AggregatedMetrics` exposes empty metrics, empty detection, operations per second, average locks per shard, and a simple performance `is_healthy` heuristic.

Control flow: shards call record methods during acquisition/release/cleanup; the manager snapshots each shard and asks `GlobalMetrics` to aggregate. Max wait time uses a relaxed compare-exchange loop. Health is derived from fast-path rate over 80%, timeout rate under 5%, and average wait under 10 ms.

State and persistence behavior: all counters are atomic process-local state. Ordering is `Relaxed` for counters and max wait, so metrics are approximate under concurrency and should not be treated as linearizable accounting. Uptime comes from `Instant` and resets on process restart.

Dependencies and integration points: used by `LockShard` for shard-level counters, `FastObjectLockManager` for aggregation and cleanup-run accounting, `DisabledLockManager` for empty metrics, and exposed through crate exports as `AggregatedMetrics`. `guard.rs` separately updates `rustfs_io_metrics` held-lock gauges, so there are two metrics surfaces.

Risks: wait-time counters are only meaningful when slow-path code calls `record_wait_time`; current shard code records slow-path success/timeouts but does not visibly record elapsed wait time, so average wait health may underreport latency. `avg_locks_per_shard` uses cumulative acquisitions, not current active locks, so the name can mislead dashboards. `is_healthy` returns false for idle metrics because fast-path rate is 0, which can make a quiet but healthy system look unhealthy.

Test signals: unit tests cover basic shard counters and global aggregation. Higher-value signals are workload tests that assert timeout rates and fast-path rates under read-heavy, write-heavy, and contention-heavy scenarios, plus metrics consistency after cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/metrics.rs -->
