# sources/storage-engines/tikv/components/raftstore/src/store/region_snapshot.rs

## Purpose
`region_snapshot.rs` wraps an engine snapshot so reads and iterators are constrained to a single TiKV region. It translates logical user keys to TiKV data keys, enforces region boundaries, exposes apply-index/data-version metadata, and supplies a region-aware iterator for scans and reverse scans.

## Important APIs, Types, and Functions
`RegionSnapshot<S: Snapshot>` owns an `Arc<S>` engine snapshot, `Arc<Region>`, lazily cached apply index, a `from_v2` data-version mode flag, optional raft term, transaction extra operation, optional transaction extensions, optional bucket metadata, and an optional observed snapshot hook. Constructors include `new(&PeerStorage)`, `from_raw(db, region)`, and `from_snapshot(snap, region)`.

Important methods include `set_observed_snapshot`, `replace_snapshot`, `get_region`, `get_snapshot`, `set_from_v2`, `get_data_version`, `set_apply_index`, `get_apply_index`, `iter`, `scan`, `get_start_key`, and `get_end_key`. The `Peekable` implementation provides bounded `get_value_opt` and `get_value_cf_opt`.

`RegionIterator<S>` wraps the engine iterator and region metadata. It exposes RocksDB-style iterator methods: `seek_to_first`, `seek_to_last`, `seek`, `seek_for_prev`, `prev`, `next`, `key`, `value`, `valid`, and `should_seekable`. Helper functions `update_lower_bound` and `update_upper_bound` clamp iterator bounds to encoded region boundaries.

## Control Flow
Point reads validate that the logical key belongs to `[region.start_key, region.end_key)` via engine utility checks, encode it with `keys::data_key`, and delegate to the underlying snapshot. On engine errors, `handle_get_value_error` increments critical-error metrics and either panics with a panic marker or logs and returns the engine error depending on TiKV's unexpected-key/data panic configuration.

Apply index is loaded lazily. `get_apply_index` returns the cached atomic value if nonzero; otherwise `get_apply_index_from_storage` reads `RaftApplyState` from CF_RAFT using the region id, stores the applied index back into the atomic, and returns it. `get_data_version` returns the underlying snapshot sequence number in v2 mode, rejecting zero, otherwise the apply index.

For scans, `scan` builds data-key lower/upper bounds from logical keys, creates a `RegionIterator`, seeks to the start key, and loops until the callback returns false or the iterator is exhausted. `RegionIterator::new` clamps any caller-provided bounds against `enc_start_key(region)` and `enc_end_key(region)` before creating the engine iterator. `seek` and `seek_for_prev` enforce inclusive region seekability, encode the seek key, and delegate to the engine iterator. Returned keys are decoded back to origin keys with `keys::origin_key`.

`replace_snapshot` consumes the wrapper, extracts the inner snapshot with `Arc::into_inner`, optionally transfers the observed snapshot hook, and builds a new `RegionSnapshot<Sp>`. It intentionally panics if the snapshot has already been cloned, preserving ownership assumptions for replacement.

## State and Persistence Behavior
This module is read-only with respect to user data. Its only mutation is local metadata caching (`apply_index`) and wrapper replacement. It reads persisted apply state from CF_RAFT when needed. Iterator bounds are encoded data-key bounds, so region isolation depends on correct key encoding and correct region metadata supplied by `PeerStorage` or callers.

## Dependencies and Integration Points
The file depends on `engine_traits` snapshot, iterator, read options, metrics, and range checks; `keys` data-key encoding; `kvproto` region/apply-state messages; PD bucket metadata; TiKV critical-error/panic hooks; and `PeerStorage`. It integrates directly with coprocessor observed snapshots, transaction extension metadata, and read paths that need a `Peekable`/iterable view limited to a region.

## Risks and Edge Cases
Region boundary handling is the core risk. Point gets use exclusive end-key checks, while iterator `should_seekable` allows inclusive checks so `seek(end_key)` can legally produce no result at the boundary. Incorrect lower/upper-bound prefix handling could leak keys outside a region or hide in-range keys. `replace_snapshot` will panic if clones exist; callers must use it before sharing the snapshot. Malformed or missing apply state causes data-version errors. Error handling can intentionally panic under strict corruption-detection settings.

## Test Signals
Tests cover point reads inside and outside a region, seek/seek-for-prev behavior across lower and upper bounds, multi-level flushed/compacted datasets, forward scans with early termination, whole-range behavior for the last region with empty end key, iterator upper bounds, and reverse iteration with lower bounds. These tests directly exercise region isolation around boundary keys.
