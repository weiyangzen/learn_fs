# sources/storage-engines/tikv/src/storage/read_pool.rs

## Purpose
This file builds the three storage read thread pools used for low, normal, and high priority read commands. It attaches per-thread engine TLS, marks I/O as foreground reads, and flushes read metrics through a pool ticker.

## Important APIs, Types, and Functions
- `FuturePoolTicker<R>` stores a `FlowStatsReporter`.
- `PoolTicker::on_tick` calls `metrics::tls_flush`.
- `build_read_pool` converts `StorageReadPoolConfig` into three YATP configs and builds pools named `store-read-low`, `store-read-normal`, and `store-read-high`.
- `build_read_pool_for_test` builds the same pool layout using `DefaultTicker`.

## Control Flow
Both builders assert that config expansion returns exactly three pool configs. For each config/name pair, they clone the reporter and engine, wrap the engine in `Arc<Mutex<_>>`, configure a `YatpPoolBuilder`, and install lifecycle hooks. `after_start` stores the engine in thread-local storage and sets `IoType::ForegroundRead`; `before_stop` destroys TLS for the engine type.

## State and Persistence Behavior
No persistent state is written. Runtime state is thread-local engine handles, thread-local metrics, pool workers, and file-system I/O type tagging. The `Arc<Mutex<E>>` is only used to clone the engine safely inside worker start hooks.

## Dependencies and Integration Points
This module depends on `StorageReadPoolConfig`, storage engine traits (`Engine`, `FlowStatsReporter`, TLS setters/destructors), `file_system::set_io_type`, and TiKV's YATP pool utilities. Schedulers use the returned `Vec<FuturePool>` to route read work by priority.

## Risks
The `assert_eq!(configs.len(), 3)` makes config shape a hard invariant. The unsafe `destroy_tls_engine::<E>()` relies on setting and destroying the same concrete engine type. If `after_start` panics on the mutex or engine clone, workers may fail to initialize. Metrics flushing depends on ticker execution.

## Test Signals
The file has no local tests. Relevant verification is construction from default/test configs, worker lifecycle behavior, TLS engine availability inside read tasks, foreground I/O tagging, and metrics flush behavior under real read workloads.
