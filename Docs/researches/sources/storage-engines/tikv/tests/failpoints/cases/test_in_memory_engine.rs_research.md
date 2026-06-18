# sources/storage-engines/tikv/tests/failpoints/cases/test_in_memory_engine.rs

## Purpose
This file is a regression suite for TiKV's hybrid in-memory region cache engine. It verifies that cached regions can be loaded, read by coprocessor point queries, updated by apply write batches, evicted or reloaded on topology changes, and kept consistent through split, merge, rollback, flashback, delete-range, SST ingest, leader transfer, and peer destruction events.

## Important APIs, Types, and Functions
- `copr_point_get`, `must_copr_point_get`, `must_copr_point_get_empty`, and `must_copr_load_data` build TiDB DAG requests against `ProductTable` data and assert whether reads observe rows through the coprocessor path.
- `async_put` starts data loading in a separate thread and is used to create deterministic races with apply and cache-load failpoints.
- `RegionCacheEngine`, `RegionCacheEngineExt`, `CacheRegion`, `EvictReason`, and `DATA_CFS` are the main cache-engine contracts under test.
- `new_server_cluster_with_hybrid_engine`, `configure_for_merge`, `new_region`, `new_peer`, `new_learner_peer`, and `Callback` are the raftstore test harness integration points.
- The tests use many IME-specific failpoints, including `ime_on_snapshot_load_finished`, `ime_on_iterator_seek`, `ime_on_region_cache_write_batch_write_impl`, `ime_on_load_region`, `ime_background_check_load_pending_interval`, `ime_fail_to_schedule_load`, and `on_apply_in_memory_engine_load_region`.

## Control Flow
The file starts with helper routines that translate table rows into coprocessor reads and writes. The tests then move through cache lifecycle scenarios: manual cache region registration, explicit `load_region`, snapshot-load completion, cached iterator verification, split-time range correction, write-batch races, cache eviction, and reload. Later tests drive merge and rollback events, leader transfers with warmup, SST ingestion, flashback, delete ranges, apply-fsm change handling, and peer destroy messages. Most tests follow the same pattern: build a small cluster, configure raftstore/apply concurrency, inject a failpoint to pause a narrow stage, mutate region state, then assert cache hit/miss behavior through `snapshot`, `region_cached`, or coprocessor iterator failpoint signals.

## State and Persistence Behavior
The suite validates that cached metadata tracks region id, epoch version, range boundaries, safe points, and manual load ranges. Split tests prove pending snapshot loads are narrowed to real post-split regions and do not wrongly cache the old super-range. Merge and rollback tests verify cached source/target regions are evicted or reloaded after epoch changes. SST ingest, delete range, unsafe destroy range, flashback, and peer tombstone paths must invalidate cached data so stale in-memory snapshots are not served. Warmup tests check that leader transfer can block until cache warmup finishes but eventually proceeds on timeout. Destroy-uninitialized-peer tests ensure cache observers tolerate peers without initialized region state.

## Dependencies and Integration Points
The file depends on Rocks SST writer/importer APIs, `engine_traits` cache abstractions, `in_memory_engine::test_util`, TiKV raftstore cluster utilities, PD client region management, coprocessor DAG helpers, and TiDB datum encoding. It integrates cache-engine behavior with raft apply tasks, raft command callbacks, import SST commands, GC worker unsafe destroy range, flashback admin commands, and raft message routing.

## Risks and Test Signals
The main risks are stale cached reads after region epoch changes, missing eviction after destructive operations, deadlocks or permanent stalls during warmup, and panics from uninitialized peer lifecycle events. Positive test signals include receiving `ime_on_iterator_seek` when reads should hit IME, `snapshot(...).is_err()` after eviction, successful `eventually` checks after reload, and row absence after delete/flashback. Several tests are race-sensitive and use sleeps, sync channels, and apply failpoints; failures often indicate subtle ordering bugs rather than simple data-path errors.
