# sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/mod.rs

Purpose: TiKV builder and runner integration for YATP pools, including lifecycle hooks, per-thread setup, task schedule latency metrics, priority/multilevel queues, cleanup scheduling, and periodic ticker callbacks.

Important APIs/types/functions: `CleanupMethod`, `PoolTicker`, `TickerWrapper`, `DefaultTicker`, `Config`, `TaskScheduleHistograms`, `YatpPoolRunner`, and `YatpPoolBuilder`.

Control flow: builders configure thread counts, stack, max tasks, queue type, cleanup strategy, hooks, and metrics. Runner `start` installs thread hooks, thread group properties, thread memory accessor, and allocator arena; `handle` records wait and execution durations around YATP future runner handling; `end` flushes ticker and removes thread bookkeeping.

State and persistence: in-memory pool configuration, local histograms flushed on ticks/end, optional cleanup futures scheduled locally or remotely.

Dependencies/integration: bridges `yatp`, TiKV resource control metadata, allocator hooks, thread maps, global timer, and worker pools.

Risks: local histogram flushing depends on task/tick activity; cleanup strategy changes where long-lived cleanup futures execute; hook closures must be thread-safe and non-panicking.

Test signals: tests cover schedule-wait recording and cleanup execution for in-place, local, and remote strategies.
