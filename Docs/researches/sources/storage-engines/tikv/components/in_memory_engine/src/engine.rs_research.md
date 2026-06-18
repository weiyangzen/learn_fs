# sources/storage-engines/tikv/components/in_memory_engine/src/engine.rs

## Purpose

Defines the in-memory region cache engine and its core storage abstraction. It mirrors selected RocksDB region data into three global skiplist CFs, exposes TiKV `RegionCacheEngine`/`RegionCacheEngineExt` behavior, handles region lifecycle events, and connects foreground writes to background loading/deletion.

## Important APIs, Types, And Functions

`cf_to_id`, `id_to_cf`, and `is_lock_cf` map TiKV CF names to skiplist indexes. `SkiplistHandle` wraps a `crossbeam_skiplist::SkipList<InternalBytes, InternalBytes>` and provides guarded `get`, `get_with_user_key`, `insert`, `remove`, iterator, and size access. `SkiplistEngine` owns the three CF skiplists for default, lock, and write data; `delete_range_cf` and `delete_range` remove all entries for a `CacheRegion`, using non-MVCC boundaries for lock CF and MVCC boundaries for default/write CFs.

`RegionCacheMemoryEngineCore` owns `SkiplistEngine` and `RegionManager`. Its `prepare_for_apply` is the key foreground gate: it decides whether a region is cached, loading, pending, evicted, outdated, or absent; updates `being_written` flags; and schedules background load from a RocksDB snapshot when a pending region first transitions to loading. `RegionCacheMemoryEngine` owns the core, background manager, optional `RocksEngine`, memory controller, statistics, config, and lock-CF tombstone byte counter. Public methods include `new`, `with_region_info_provider`, `new_region`, `load_region`, `evict_region`, `bg_worker_manager`, `memory_controller`, `statistics`, and `start_cross_check`.

## Control Flow

Construction requires `config.value().enable`, creates a shared core and `MemoryController`, then starts `BgWorkManager` with optional region info and raft casual router. `set_disk_engine` stores the RocksDB handle and notifies the background runner. `snapshot` delegates to `RegionCacheSnapshot::new`, which verifies region/read constraints in the read module.

When foreground apply calls `prepare_for_apply`, the fast path reads region metadata and returns `Cached`, `Loading`, or `NotInCache` without write-locking if possible. The slow path handles pending regions, outdated epoch versions, flashback cancellation, and scheduling of `BackgroundTask::LoadRegion`. The method captures the RocksDB snapshot only after dropping region-manager locks to avoid long lock holds. Region events drive state transitions: `Eviction` calls `evict_region` and schedules deletion for immediately deletable regions, `TryLoad` optionally respects manual load ranges, `Split` delegates to `RegionManager::split_region`, and `EvictByRange` evicts all overlapped cached regions.

## State And Persistence Behavior

All cache data is volatile skiplist state. The durable source of truth remains the disk engine. Region metadata records cache state, epochs, ranges, snapshots, writes in progress, eviction reasons, and safe points. Eviction makes a region unreadable immediately through metadata, but data may remain in skiplists until delayed delete-range work can safely run. Writes are mirrored through `write_batch.rs` and must attach `MemoryController` handles to inserted `InternalBytes` so memory is released on drop.

## Dependencies And Integration Points

Depends on `crossbeam_skiplist`, crossbeam epoch guards, `engine_rocks::RocksEngine`, `engine_traits` region cache traits and CF constants, `pd_client`, raftstore `RegionInfoProvider`/`CasualRouter`, local `background`, `keys`, `memory_controller`, `read`, `region_manager`, and `statistics`. It is the primary type re-exported by `lib.rs` as `RegionCacheMemoryEngine`.

## Risks

The region state machine is central and race-prone: pending regions can become outdated, split, flashback-canceled, evicted, or loaded while writes are in flight. `prepare_for_apply` unwraps `rocks_engine` when scheduling load, so callers must set a disk engine before loading can actually occur. Skiplist delete boundaries differ by CF; using the wrong boundary encoding can delete too much or leak keys. Deletion is eventual, so memory may remain above thresholds until snapshots/writes/GC release. Public `must_set_region_state` is benchmark-only and bypasses normal invariants.

## Test Signals

Tests verify outdated epoch overlap handling, delete-range behavior for default/write and lock CFs, active/inactive region transitions across split and eviction, and eviction callbacks blocked by active snapshots. These tests complement background and write-batch failpoint tests that exercise the same engine state machine.
