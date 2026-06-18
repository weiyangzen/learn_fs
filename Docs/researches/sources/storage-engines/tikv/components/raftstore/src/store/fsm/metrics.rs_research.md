# sources/storage-engines/tikv/components/raftstore/src/store/fsm/metrics.rs

## Purpose

`sources/storage-engines/tikv/components/raftstore/src/store/fsm/metrics.rs` defines a small set of raftstore FSM metrics and shared store-stat aggregation types. It bridges hot-path per-poller accounting with global atomics that the store heartbeat and maintenance ticks can consume without locking every write operation.

The file was read completely as a 122-line Rust module. It contains a Prometheus histogram for apply proposal batch size and the `StoreStat` / `GlobalStoreStat` / `LocalStoreStat` aggregation pattern.

## Important APIs, Types, and Functions

`APPLY_PROPOSAL` is a lazily registered Prometheus `Histogram` named `tikv_raftstore_apply_proposal`. It observes the count of proposals sent by a region at once using exponential buckets from 1 to 2^19. The apply FSM observes it after draining proposals into pending commands.

`StoreStat` is the global atomic storage for raftstore write-flow and busy-state metrics: `lock_cf_bytes_written`, `engine_total_bytes_written`, `engine_total_keys_written`, `engine_total_query_put`, `engine_total_query_delete`, `engine_total_query_delete_range`, and `is_busy`. All fields use atomics so multiple pollers or local flushes can update shared counters cheaply.

`GlobalStoreStat` wraps `Arc<StoreStat>` and exposes `local(&self) -> LocalStoreStat`, creating a zeroed local accumulator tied back to the same global stat object.

`LocalStoreStat` stores non-atomic local counters for one poll context: lock CF bytes, total written bytes, total written keys, `tikv_util::store::QueryStats`, and an `is_busy` flag. Its custom `Clone` does not duplicate accumulated values; it returns a fresh zeroed local accumulator for the same global object.

`LocalStoreStat::flush(&mut self)` transfers non-zero local counters into the global atomics with relaxed ordering, clears the local counters, and sets the global `is_busy` flag to true if the local poller observed busy state.

## Control Flow

`RaftPoller::end` in `store/fsm/store.rs` calls `self.poll_ctx.store_stat.flush()`, so local metrics accumulated during raft processing are periodically folded into `GlobalStoreStat`. Peer execution updates write counters after command execution results have fully completed, avoiding double counting around commit-merge waits.

The store heartbeat path in `store/fsm/store.rs` consumes global counters with atomic `swap(0, Ordering::Relaxed)` for bytes, keys, query stats, and busy state, then writes those values into `pdpb::StoreStats` for PD. The lock-CF compaction tick reads `lock_cf_bytes_written` with `SeqCst` and subtracts the observed total when scheduling a full lock CF compaction.

`APPLY_PROPOSAL` is observed in `store/fsm/apply.rs` after proposals have been converted into pending commands. The metric is intentionally independent from `StoreStat`; it is an immediate Prometheus histogram, not part of PD store heartbeat stats.

## State and Persistence Behavior

This module owns no persistent state and performs no engine I/O. Its state is process-local telemetry. Local accumulators live inside raftstore poll contexts; global atomics live behind an `Arc` shared by the raftstore system.

Most flush operations use `Ordering::Relaxed` because the counters are telemetry and do not guard correctness-critical memory. `lock_cf_bytes_written` uses stronger ordering in the consuming compaction path, but local flush still uses relaxed `fetch_add`. The busy flag is level-like between heartbeats: any local busy observation stores true globally, and the heartbeat consumes it with `swap(false, Relaxed)`.

## Dependencies and Integration Points

Direct dependencies are `std::sync::{Arc, atomic::*}`, `lazy_static`, `prometheus::{Histogram, exponential_buckets, register_histogram}`, and `tikv_util::store::QueryStats`.

The module is re-exported by `store/fsm/mod.rs` as `GlobalStoreStat` and `LocalStoreStat`. `RaftPollerBuilder` initializes `GlobalStoreStat::default()`, `PollContext` carries both global and local stats, peer FSM command execution increments local write counters, raft poller shutdown/end-of-iteration flushes them, and store heartbeat reports the global values to PD. Lock CF compaction uses the lock-CF byte counter to schedule cleanup work.

## Risks and Edge Cases

Because `LocalStoreStat::clone` drops local accumulated values and returns a fresh zeroed accumulator, callers must not clone it expecting a snapshot. In this codebase it is used as a context-local accumulator, and the custom clone avoids accidental double counting.

Counters can be temporarily underreported if a poller exits or stalls before `flush`. The design accepts eventual telemetry accuracy in exchange for avoiding atomics on every hot-path mutation.

`flush` only clears the `put`, `delete`, and `delete_range` fields of `QueryStats`; if `QueryStats` grows additional fields, this code must be updated or new query counters will never reach PD stats.

The lock-CF compaction path subtracts the loaded total after scheduling. Concurrent relaxed additions can race with the load/subtract window; as telemetry-driven thresholding this is acceptable, but changes here should avoid making compaction scheduling depend on exact accounting.

## Test Signals

Unit tests should verify that `GlobalStoreStat::local` starts at zero, `LocalStoreStat::flush` adds each counter to the matching global atomic, clears local fields, and sets/clears busy state as expected. A focused test should assert that cloning a `LocalStoreStat` does not carry over accumulated counters.

Integration signals include store heartbeat tests that confirm bytes, keys, query stats, and busy state are swapped into `StoreStats`, peer execution tests that update `ctx.store_stat` only after command results complete, and lock-CF compaction tests that schedule cleanup only after the threshold is exceeded.

Metrics smoke tests can validate that `APPLY_PROPOSAL` registration succeeds and observations from apply proposal draining appear in the histogram without panics or duplicate registration.
