# sources/storage-engines/tikv/components/in_memory_engine/src/prop_test.rs

## Purpose

This file property-tests the skiplist-backed in-memory engine against RocksDB for basic put/get/delete/scan/delete-range behavior across default, lock, and write CFs. It also provides `new_skiplist_engine_for_test`, a shared helper used by other test modules.

## Important APIs, Types, And Functions

- `new_skiplist_engine_for_test` creates a `SkiplistEngine`, a high-capacity `MemoryController`, and a closure that encodes raw key/value inputs into `InternalBytes` with controller ownership and an epoch guard.
- `Operation` models generated mutations and reads.
- `gen_operations` generates CF plus operation vectors with bounded key/value sizes.
- `scan_rocksdb` and `scan_skiplist` normalize scan results for comparison.
- `test_rocksdb_skiplist_basic_operations` replays generated operations against RocksDB and the skiplist and asserts equivalent visible results.

## Control Flow

The property test generates a CF and up to 100 operations. For default/write CFs it appends a fixed MVCC suffix to raw keys before writing both engines, because skiplist delete-range semantics account for MVCC suffixes. Puts insert into RocksDB and the skiplist; gets compare RocksDB optional value with skiplist lookup; scans seek both engines and compare ordered key/value vectors; delete-range normalizes range endpoints, constructs a `CacheRegion`, deletes from skiplist, then deletes the MVCC-suffixed range from RocksDB.

## State And Persistence Behavior

RocksDB state lives in a temporary directory and is discarded. Skiplist state is memory-only and protected by crossbeam epoch guards. The helper configures very high test capacity/evict thresholds to keep memory-control behavior from interfering with correctness comparisons.

## Dependencies And Integration Points

The file depends on `engine_rocks`, `engine_traits`, `proptest`, `crossbeam::epoch`, `txn_types`, `tikv_util::config::VersionTrack`, local key encode/decode helpers, `MemoryController`, and `SkiplistEngine`. `memory_usage_test.rs` also imports `new_skiplist_engine_for_test`.

## Risks And Edge Cases

The generated get/delete/scan keys can be empty even though put keys are non-empty; this intentionally probes boundary behavior but does not cover all TiKV key encoding invariants. The fixed `MVCC_SUFFIX` means generated tests compare one simplified MVCC shape. Delete-range behavior differs by CF and depends on correct endpoint ordering after swapping `k1` and `k2`.

## Test Signals

The proptest runs 100 generated cases and there is a fixed regression `test_case1` for a prior delete-range/scan interaction in write CF. This is a high-value behavioral oracle for low-level skiplist operations.
