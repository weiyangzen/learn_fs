# sources/storage-engines/tikv/components/in_memory_engine/tests/failpoints/test_memory_engine.rs

## Purpose
This file exercises in-memory-engine behavior under injected timing and failure conditions. It targets the parts that are difficult to validate with straight-line unit tests: disk-engine setup, GC, tombstone cleanup, snapshot load/evict races, delete-range scheduling, region split during load, and eviction callbacks.

## Important APIs, Types, and Functions
Tests construct `RegionCacheMemoryEngine` with test configs, attach RocksDB engines via `set_disk_engine`, create regions with `new_region`, write via `engine.write_batch`, and inspect skiplist CF handles. Helpers include `key_exist` for sequence-suffixed skiplist keys and closures that count internal keys in encoded region boundaries. Failpoints such as `ime_set_rocks_engine`, `ime_gc_oldest_seqno`, `ime_on_snapshot_load_finished`, `ime_before_clear_regions_in_being_written`, and `ime_on_delete_range` coordinate racing tasks.

## Control Flow
The tests commonly set failpoint callbacks/channels, prepare engine state, trigger async background work through writes or explicit background tasks, then block on channels or `eventually` polling. Race-oriented tests pause background operations, assert intermediate state, remove failpoints, and assert eventual cleanup or active state. Stream-like flows are not used; synchronization is via sync channels, Tokio channels, and failpoint callbacks.

## State and Persistence Behavior
The tests write both RocksDB data and in-memory skiplist data. They verify that loading filters MVCC history by safe point, GC removes old versions, lock tombstone cleanup keeps versions newer than the snapshot sequence, failed loads remove region metadata, and evictions delete in-memory range data only after active writers leave in-written state. Temporary RocksDB directories isolate persistence per test.

## Dependencies and Integration Points
The file integrates `engine_rocks`, `engine_traits`, `keys`, `txn_types`, Tokio, crossbeam epoch guards, and the in-memory-engine test utilities. It is tightly coupled to background task failpoint names and region manager states such as `Loading`, `Active`, and eviction states.

## Risks
The tests assume failpoint callbacks are reached within short deadlines; timing-sensitive regressions may appear as flakes. Some assertions inspect internal skiplist ordering and counts, so changes to internal key encoding or GC retention rules require test updates. Because many tests pause failpoints, missing cleanup could contaminate later tests if run in-process.

## Test Signals
Coverage is strong for concurrency boundaries: set-disk-engine callback, GC old-version removal, lock tombstone cleanup, eviction overlapping loading ranges, load failure cleanup, delete-range vs write-to-memory serialization, duplicate delete-range scheduling, load with GC safe point, region split before batch loading starts, and async eviction callback ordering.
