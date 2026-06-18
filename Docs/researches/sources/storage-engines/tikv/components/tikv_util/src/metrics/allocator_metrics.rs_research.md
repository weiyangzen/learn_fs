# sources/storage-engines/tikv/components/tikv_util/src/metrics/allocator_metrics.rs

## Purpose
Registers a custom Prometheus collector for allocator-level and allocator-thread statistics exposed by `tikv_alloc`.

## Important APIs, Types, and Functions
- `monitor_allocator_stats(namespace)` creates and registers `AllocStatsCollector`.
- `AllocStatsCollector` owns descriptor lists and four metric families: allocator stats, per-arena thread stats, per-thread allocation counters, and arena count.
- `Collector::collect` refreshes metrics from `tikv_alloc::{fetch_stats,get_arena_count,iterate_arena_allocation_stats,iterate_thread_allocation_stats}`.

## Control Flow
Collector construction creates gauge vectors with a caller-provided namespace. Every Prometheus scrape calls `collect`, which fetches allocator global stats if available, sets arena count, iterates arena resident/mapped/retained values by thread name, iterates alloc/dealloc counters, then concatenates each metric family.

## State and Persistence Behavior
Collector state is process-local Prometheus metric state. Values are overwritten on each scrape from allocator snapshots; there is no persistent storage. Missing `fetch_stats` data is silently skipped while arena and thread allocation snapshots still run.

## Dependencies and Integration Points
Depends on `prometheus` collector APIs and `tikv_alloc` allocator instrumentation. It is re-exported by `metrics/mod.rs` and usually installed during TiKV metrics initialization.

## Risks
Metric labels use allocator-provided thread names, so cardinality and stale label values depend on allocator behavior. Registration can fail on duplicate metric names. Unsupported allocator stats produce partial output rather than a hard error.

## Test Signals
No local tests in this file; integration confidence comes from Prometheus collector semantics and allocator instrumentation consumers.
