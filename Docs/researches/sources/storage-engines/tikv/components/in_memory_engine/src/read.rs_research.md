# sources/storage-engines/tikv/components/in_memory_engine/src/read.rs

## Purpose

This file implements snapshot reads and RocksDB-like iteration over the in-memory region cache. It enforces region boundaries, region epoch/safe-point validation, sequence-number visibility, tombstone handling, prefix iteration, read metrics, and delayed physical eviction while snapshots are alive.

## Important APIs, Types, And Functions

- `MAX_SEQUENCE_NUMBER` is the highest sequence used for seek construction.
- `RegionCacheSnapshotMeta` records the `CacheRegion`, read timestamp, and shared RocksDB/in-memory sequence number.
- `RegionCacheSnapshot::new` registers a region snapshot with `RegionManager` and captures the skiplist engine.
- `Drop for RegionCacheSnapshot` unregisters the snapshot and schedules `BackgroundTask::DeleteRegions` for ranges that become physically removable.
- `Iterable for RegionCacheSnapshot::iterator_opt` creates `RegionCacheIterator` with mandatory lower/upper bounds checked against the snapshot region.
- `Peekable for RegionCacheSnapshot::get_value_cf_opt` performs bounded point lookup by encoded internal seek key and sequence visibility.
- `RegionCacheIterator` implements forward/backward iteration, prefix-restricted seeks, direction reversal, sequence filtering, deletion skipping, statistics flushing, and `MetricsExt`.
- `RegionCacheDbVector` wraps `bytes::Bytes` as an engine `DbVector`.

## Control Flow

Snapshot construction first calls `region_manager.region_snapshot`, which rejects non-active, epoch-mismatched, or too-old reads. Point get checks the user key is within the cached region, seeks the CF skiplist to `encode_seek_key(key, sequence_number)`, decodes the found internal key, and returns only visible `Value` entries for the exact user key.

Iterator construction requires both bounds and rejects bounds outside the region. Forward seek uses `encode_seek_key` and `find_next_visible_key`, which walks until it finds the first visible non-deleted version for a new user key within upper bound and optional prefix. Backward seek uses `encode_seek_for_prev_key`, `prev_internal`, `find_value_for_current_key`, and `find_user_key_before_saved` to collect the latest visible value while scanning reverse through versions. `next` and `prev` handle direction reversal so callers can alternate directions in RocksDB-compatible ways. On iterator drop, local counters are flushed into global `Statistics` and thread-local `PERF_CONTEXT`.

## State And Persistence Behavior

The module does not persist data. It reads crossbeam-skiplist CFs owned by `SkiplistEngine`, tracks active read snapshots in `RegionManager`, and schedules asynchronous delete-range work when snapshot release unblocks eviction. Sequence numbers are shared with disk engine snapshots to preserve atomic write visibility across memory and RocksDB.

## Dependencies And Integration Points

The file depends on `engine_traits` snapshot/iterator/read traits, `crossbeam_skiplist`, `crossbeam::epoch`, `engine_rocks` prefix transforms, local key encoding/decoding, `RegionCacheMemoryEngine`, `BackgroundTask`, `metrics::IN_MEMORY_ENGINE_SEEK_DURATION`, `statistics`, and `perf_context`. It is the main read surface used by the engine implementation and by tests comparing behavior to RocksDB.

## Risks And Edge Cases

Iterator correctness is sensitive to internal-key ordering, sequence comparison, deletion semantics, and direction reversal. Prefix seek asserts key length at least eight bytes and disables `seek_to_first/last` via assertions when prefix mode is enabled. `iterator_opt` only supports explicit bounds; callers that omit bounds receive `Error::BoundaryNotSet`. Snapshot drops can schedule background deletion, so failures in the background scheduler leave eviction cleanup dependent on shutdown assertions/logging. `find_user_key_before_saved` calls `self.is_visible(self.sequence_number)`, which is always true for normal sequence numbers and functions as unconditional skip accounting rather than filtering the current entry.

## Test Signals

The test module is extensive: snapshot refcounts and safe points, point get with sequence-visible deletions, forward and backward iteration with bounds, sequence visibility in both directions, user-key skip corner cases, prefix seek, skiplist range eviction, eviction with/without active snapshots after split, tombstone/perf counters, read-flow metrics compared to RocksDB statistics, RocksDB iterator compatibility cases, newer-sequence behavior, and direction reversal.
