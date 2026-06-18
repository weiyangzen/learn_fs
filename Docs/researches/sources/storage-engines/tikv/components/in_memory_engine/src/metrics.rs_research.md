# sources/storage-engines/tikv/components/in_memory_engine/src/metrics.rs

## Purpose

This file defines Prometheus metrics and static auto-flush wrappers for the in-memory engine. It bridges internal ticker/statistics counters, eviction reasons, GC filtering, memory usage, load/write latencies, auto-load/evict observations, and per-CF operation counts into TiKV's metrics surface.

## Important APIs, Types, And Functions

- Static label enums model GC count types, ticker names, eviction reasons, operation types, and the three TiKV CFs.
- Lazy statics register gauges, counters, counter vecs, histograms, and histogram vecs under `tikv_in_memory_engine_*` names plus `tikv_safe_point_gap_with_in_memory_engine`.
- `flush_in_memory_engine_statistics` drains global `InMemoryEngineStatistics` ticker counters and forwards them to metric counters.
- `flush_engine_ticker_metrics` maps `Tickers` variants to flow/locate metric labels.
- `observe_eviction_duration` maps every `engine_traits::EvictReason` variant to the matching eviction-duration label.
- `count_operations_for_cfs` records put/delete counts for default, lock, and write CFs.

## Control Flow

Metrics are registered at first lazy-static access. Runtime code records low-cost local static metrics and periodically calls flush helpers. `flush_in_memory_engine_statistics` iterates `ENGINE_TICKER_TYPES`, atomically drains each ticker through `get_and_reset_ticker_count`, then dispatches the value by match. Eviction completion calls `observe_eviction_duration`, and write accounting calls `count_operations_for_cfs` with fixed CF-indexed arrays.

## State And Persistence Behavior

Metrics are process-local Prometheus state; no persistent state is maintained. `flush_in_memory_engine_statistics` is destructive for ticker counters because it resets them after reading, while gauges and histograms retain standard Prometheus in-process state.

## Dependencies And Integration Points

The file depends on `prometheus`, `prometheus_static_metric`, `lazy_static`, `engine_traits::EvictReason`, and local `statistics::{Tickers, ENGINE_TICKER_TYPES}`. It is integrated by read iterators, region eviction completion, memory-controller/reporting code, GC/load/write paths, and auto-load/evict policy code in `region_stats.rs`.

## Risks And Edge Cases

The match in `flush_engine_ticker_metrics` treats any ticker outside `ENGINE_TICKER_TYPES` as unreachable, so the ticker list and enum mapping must stay synchronized. `count_operations_for_cfs` asserts both arrays have length three and relies on `cf_to_id` ordering: default, lock, write. Any new `EvictReason` requires adding a static label and match arm or compilation will fail. Static metric registration uses `unwrap`, so duplicate metric names would panic at initialization.

## Test Signals

There are no local tests in this file. Coverage comes indirectly from read-flow tests in `read.rs`, statistics tests in `statistics.rs`, and eviction paths in `region_manager.rs`/`region_stats.rs` that exercise metric update paths.
