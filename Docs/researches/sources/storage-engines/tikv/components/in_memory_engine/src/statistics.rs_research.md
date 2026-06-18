# sources/storage-engines/tikv/components/in_memory_engine/src/statistics.rs

## Purpose

This file implements low-overhead in-memory engine ticker statistics. It uses core-local padded counters to reduce contention for hot read/iterator metrics, then provides aggregate and drain operations for metrics flushing.

## Important APIs, Types, And Functions

- `CoreLocalArray<T>` allocates a power-of-two array of per-core values, at least eight entries.
- `physical_core_id` uses `libc::sched_getcpu` on Linux x86_64 and falls back to `-1` elsewhere.
- `Tickers` enumerates bytes read, iterator bytes read, seek/next/prev counts, and found counts.
- `ENGINE_TICKER_TYPES` lists the tickers exported by metrics flushing.
- `StatisticsData` wraps atomic ticker counters.
- `Statistics` provides `record_ticker`, `get_ticker_count`, and `get_and_reset_ticker_count`.
- `LocalStatistics` accumulates per-iterator counters before a single flush on iterator drop.

## Control Flow

Hot paths call `Statistics::record_ticker`, which selects a core-local shard from the current CPU id or a random shard fallback and performs relaxed atomic addition. Aggregate readers lock `_aggregate_lock` and sum all shards. Drain operations also hold the lock and `swap(0)` every shard for the selected ticker. Iterators avoid per-step atomics by updating `LocalStatistics`, then flushing the totals when dropped.

## State And Persistence Behavior

Statistics are process-local and non-persistent. `get_and_reset_ticker_count` clears the selected counter across all shards, so callers use it for periodic Prometheus delta export. Relaxed atomics are sufficient because counters are approximate telemetry rather than correctness state, while the mutex serializes aggregate/drain operations.

## Dependencies And Integration Points

The module depends on `crossbeam::utils::CachePadded`, `rand`, `libc`, standard atomics and mutexes. It integrates with `metrics.rs` for Prometheus flushing and `read.rs` for point-read and iterator accounting.

## Risks And Edge Cases

The core-local index can be inaccurate after thread migration; this is accepted for performance. Non-Linux or failed `sched_getcpu` paths select random shards, reducing locality. Adding a new `Tickers` variant requires updating `TickerEnumMax`, `ENGINE_TICKER_TYPES`, and `metrics.rs` label mapping. Aggregate locking prevents concurrent drains from interleaving, but relaxed increments can still race with drains in the usual telemetry sense.

## Test Signals

`test_core_local` spawns four threads, records two ticker types, validates aggregate totals, verifies drain values, and confirms counters reset to zero after `get_and_reset_ticker_count`.
