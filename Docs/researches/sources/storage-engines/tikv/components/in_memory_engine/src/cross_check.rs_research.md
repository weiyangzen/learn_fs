# sources/storage-engines/tikv/components/in_memory_engine/src/cross_check.rs

## Purpose

Provides a periodic consistency auditor for test/debug use. It compares in-memory engine snapshots against RocksDB snapshots under MVCC snapshot semantics, allowing only differences that are valid because IME GC, RocksDB/TiKV GC, rollback/lock writes, delete markers, or region metadata changes have occurred.

## Important APIs, Types, And Functions

`CrossChecker` owns a PD client, `RegionCacheMemoryEngine`, `RocksEngine`, check interval, and a callback for TiKV's safe point. `StopReason` reports non-panic early exits: `RegionMetaChanged`, `KeyGcInRocksDB`, and `TiKVSafepointGetFailed`. `CrossCheckTask::CrossCheck` is the timer task. The main method `cross_check_region` compares `CF_LOCK` and `CF_WRITE` between a `RegionCacheSnapshot` and `RocksSnapshot`. Helpers `check_with_key_in_disk_iter`, `check_remain_disk_key`, and `check_duplicated_mvcc_version_for_last_user_key` implement alignment and validity rules. `KeyCheckingInfo` records MVCC versions for one user key and the latest version at or below the active safe point.

## Control Flow

On each timer, `run` collects active regions, takes one RocksDB snapshot, asks PD for a TSO, chooses a read timestamp one minute in the past, and builds IME snapshots using the RocksDB snapshot sequence number. It then audits each region. For every CF, it creates bounded iterators over the region range. Lock CF must match key/value exactly, because it is not subject to MVCC write-CF filtering. Write CF can diverge only in narrowly checked ways: rollback and lock writes may be absent, versions below the IME safe point may be filtered when a newer retained version or delete marker makes them invisible, and in-memory keys absent from disk can stop the check if TiKV's global safe point implies RocksDB already GCed them.

The checker advances the disk iterator until it aligns with the current memory key. Each skipped disk key is parsed as a `WriteRef` and checked against the current safe point, current/previous user-key MVCC recordings, delete-marker state, and region metadata. If a disk key newer than the safe point is missing from IME, or a lower version below the safe point was filtered without a valid retaining version/delete marker, the checker panics. For write-CF `Put` entries without short values, it also validates that the corresponding default-CF value exists in the memory snapshot.

## State And Persistence Behavior

Cross-checking is read-only. It snapshots RocksDB and IME state, consults the current region safe point from region metadata, and may refresh that safe point during comparison. It does not repair state or persist results; failures are expressed as panics for invariant violations or logged stop reasons for expected races/GC cases.

## Dependencies And Integration Points

Started by `BackgroundTask::TurnOnCrossCheck` in `background.rs` when `InMemoryEngineConfig.cross_check_interval` is nonzero. It depends on `engine_traits` iterators and cache snapshots, `engine_rocks`, PD TSO, `txn_types::{Key, TimeStamp, WriteRef, WriteType}`, `background::{split_ts, parse_write}`, and the local read snapshot/iterator implementation. `RegionCacheMemoryEngine::start_cross_check` is the external entry point.

## Risks

The auditor intentionally panics on mismatches, so enabling it outside controlled test/debug contexts can crash a process. It assumes sorted MVCC iteration and exact lock-CF parity. Safe points can move while auditing; region splits or evictions are handled as stop reasons, but other races may make failures difficult to interpret. TiKV safe-point callback absence or stale values can cause false positives/early exits. The logic is complex around delete markers and duplicated versions; future GC/filter changes must update the checker in lockstep.

## Test Signals

`test_cross_check` covers many legal divergence patterns, including rollback, delete-marker filtering, retained latest versions below safe point, temporary GC states, and user-key transitions. `test_keys_are_gced_in_rocksdb` verifies early stop when RocksDB has already GCed keys under TiKV safe point. Multiple `#[should_panic]` tests cover missing valid MVCC versions, missing newer keys, redundant IME keys, and invalid rollback/delete scenarios. These tests are the primary regression suite for checker semantics.
