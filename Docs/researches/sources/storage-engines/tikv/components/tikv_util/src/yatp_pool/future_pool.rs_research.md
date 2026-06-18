# sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/future_pool.rs

Purpose: wraps a YATP future thread pool with TiKV metrics, task-count admission control, handle-returning spawn, and tracker TLS propagation.

Important APIs/types/functions: `FuturePool`, `PoolInner`, `Full`, `spawn`, `spawn_with_extras`, `spawn_handle`, `scale_pool_size`, `set_max_tasks_per_worker`, and `get_running_task_count`.

Control flow: spawns wrap futures in `TlsTrackedFuture`, infer task priority from YATP extras, gate against the running gauge for that priority, increment running before spawn, and use `FutureExt::map` to decrement running and increment handled at completion. `spawn_handle` sends the output through a oneshot channel.

State and persistence: in-memory YATP pool, atomic pool size and max task limit, and Prometheus gauges/counters.

Dependencies/integration: used by worker pool and YATP builder; depends on `tracker`, `yatp`, resource-control task priority, failpoints, and Prometheus.

Risks: admission checks use metric gauge values, so metric-accounting bugs can affect behavior; per-priority gating compares only the selected priority count to a global max; cancellation before execution must still reach the mapped completion path to decrement.

Test signals: tests cover ticker behavior, spawn handles, running counts, full-pool rejection, and scaling.
