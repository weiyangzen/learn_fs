# sources/storage-engines/tikv/components/tikv_util/src/range_latch.rs

## Purpose
Provides mutual exclusion for overlapping key ranges, currently aimed at avoiding concurrent RocksDB compaction-filter writes and ingest-SST operations over the same keyspace.

## Important APIs, Types, and Functions
- `RangeLatch` owns `Mutex<BTreeMap<Vec<u8>, (Arc<Mutex<()>>, (Vec<u8>, Vec<u8>))>>`.
- `RangeLatch::acquire(start_key, end_key)` blocks until no overlapping active range exists and returns `RangeLatchGuard`.
- `RangeLatchGuard` removes the active range entry on drop.

## Control Flow
Acquisition locks the range map, scans entries with start keys before the requested end key, filters true overlaps, and either inserts a new latch mutex or drops the map lock and waits on each overlapping range mutex. It loops until a conflict-free insert succeeds. The guard holds the range-specific mutex and removes its map entry when dropped.

## State and Persistence Behavior
Active latch state is in memory only. Ranges are keyed by start key and removed when guards drop. `ManuallyDrop` and lifetime transmute are used to ensure the mutex guard is dropped before the backing `Arc<Mutex<()>>` can be removed.

## Dependencies and Integration Points
Uses standard `BTreeMap`, `Mutex`, `Arc`, and range bounds. It integrates with RocksDB ingest/compaction-filter coordination where concurrency is low and range conflicts are rare.

## Risks
The code documents possible livelock under repeated conflicting acquisitions, though deadlock is avoided because threads wait on one range mutex at a time. Duplicate start keys are asserted absent; overlapping ranges with identical starts cannot coexist. The lifetime transmute is unsafe-adjacent and depends on drop ordering enforced manually.

## Test Signals
Tests cover non-overlapping single-thread ranges, several overlap shapes with blocking/unblocking behavior, and randomized concurrent range acquisition to assert no active overlaps.
