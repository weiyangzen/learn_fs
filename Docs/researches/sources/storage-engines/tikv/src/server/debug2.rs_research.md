# sources/storage-engines/tikv/src/server/debug2.rs

## Purpose

`server/debug2.rs` implements the same `Debugger` trait for raftstore-v2, where raft metadata lives in a raft engine and key/value data is split into per-region tablets managed by `TabletRegistry<RocksEngine>`. It adapts classic debug operations to tablet lookup, persisted apply-index semantics, and region-range fanout.

The file shares repair primitives from `debug.rs` where possible, especially MVCC recovery and property dumping, but rewrites routing and persistence around tablet caches and raft-engine log batches.

## Important APIs, types, and functions

`DebuggerImplV2<ER>` owns a `TabletRegistry<RocksEngine>`, raft engine, optional KV/raft statistics, and `ConfigController`. Its public helpers mirror classic debugger operations: `recover_regions`, `recover_all`, `bad_regions`, `set_region_tombstone`, `set_region_tombstone_by_id`, and `drop_unapplied_raftlog`.

`MvccInfoIteratorV2` scans MVCC info across tablet boundaries. It keeps sorted active region states, the current region, requested encoded start/end bounds, a limit, and an optional `MvccInfoScanner`. `seek_region`, `smaller_key`, and `larger_key` help find the region and clipped scan range for each tablet.

`range_in_region`, `find_region_states_by_key_range`, `find_region_state_by_key`, `get_tablet_cache`, `get_all_active_region_states`, and `deivde_regions_for_concurrency` are the routing helpers that map global encoded ranges or raw keys to region/tablet work.

`new_debugger` under test/testexport builds a raftstore-v2 debugger from a TiKV config, tablet registry, and raft log engine.

## Control flow

Point reads call `find_region_state_by_key` on the key without the data prefix, load or reuse the tablet for that region, and read the requested CF from that tablet. `scan_mvcc` validates bounds, collects all non-tombstone region states, sorts them by region start key, and constructs `MvccInfoIteratorV2`; the iterator scans the current tablet until exhausted, advances to the next region by current end key, clips the requested range to the next region, and stops on limit or no further region.

`region_info` differs from classic debug: it first reads the flushed index for CF_RAFT and uses that persisted applied index to fetch apply and region state. It then overwrites `apply_state.applied_index` with the persisted applied value because that is the restart-visible state. This intentionally ignores newer apply-state records that are not visible at the persisted flushed index.

`region_size`, `get_region_properties`, and `get_range_properties` load tablets and scan only the region-overlapped encoded bounds. `compact` rejects raft DB compaction, finds all normal regions overlapping the requested encoded range, then runs RocksDB manual compaction on each tablet with clipped start/end keys.

`recover_regions` skips non-normal regions, loads each region tablet, and calls `recover_mvcc_for_range` over the region's raw start/end keys. `recover_all` groups active regions by approximate tablet size, opens all tablets for a group, and runs recovery concurrently with one thread per group.

`bad_regions` iterates raft groups, loads persisted region state, skips tombstone/applying, verifies a local peer exists, constructs raftstore-v2 `Storage`, and validates it through `RawNode::new`.

Tombstoning validates the same PD-region conditions as classic debug but writes through raft-engine log batches using the region's apply index. Tombstone-by-id also requires an apply state so it can write region state at the applied index. `drop_unapplied_raftlog` mirrors the classic algorithm but writes apply/raft state and GC records entirely through the raft engine.

## State and persistence behavior

Persistent state is split between the raft engine and per-region Rocks tablets. Region/apply/raft state and store identity are read/written via raft-engine APIs and log batches. KV data and MVCC records are read or repaired in tablets. Tablet loading uses `TabletContext` from region state and tablet index; a missing tablet can be loaded from the registry, and failures are surfaced as boxed errors.

The file does not implement `reset_to_version` or key-range flashback for raftstore-v2; both are `unimplemented!`, so calling them will panic. Config mutation still delegates to `ConfigController`. Statistics are appended from opened tablets plus optional `RocksStatistics`.

## Dependencies and integration points

This module depends on `engine_traits::{RaftEngine, TabletRegistry, CachedTablet, TabletContext}`, `raftstore_v2::Storage`, raftstore coprocessor helpers for approximate middle/size, `keys` data-prefix helpers, `debug.rs` trait/types/helpers, RocksDB compaction utilities, `ConfigController`, and MVCC scanner/collector types. It is selected for raftstore-v2 debug services and preserves the external `Debugger` trait expected by callers.

## Risks and edge cases

Several helpers unwrap raft-engine iteration results, region states, tablet latest handles, and scanner construction. `find_region_state_by_key` linearly scans raft groups and breaks if the matching region is not normal, returning not found. `get` slices `key[DATA_PREFIX_KEY.len()..]`, so callers must pass encoded data keys with the expected prefix. `MvccInfoIteratorV2` contains duplicated assertions that check `iter_start` twice and do not check `iter_end`; empty clipped ranges may panic or behave unexpectedly. The misspelled `deivde_regions_for_concurrency` is harmless but visible.

`range_in_region` accepts empty ranges and sentinel bounds as full-range requests; incorrect prefix handling would route compaction/properties to wrong tablet subranges. Raft DB compaction is explicitly disallowed in v2 even though `validate_db_and_cf` accepts `(Raft, default)` before `compact` rejects it. `recover_all` groups by approximate size, so skewed estimates can still produce uneven work.

## Test signals

Tests cover point get routing and tombstone rejection, raft log fetch, persisted-index-aware region info, region size with untrimmed tablet data, raft compaction rejection, range/region overlap clipping for first/last/full regions, even and uneven region grouping by approximate size, bad-region detection, PD-style tombstoning, tombstone-by-id, dropping unapplied raft logs including invisible newer apply-state records, and active-region listing that filters tombstones. These tests directly target raftstore-v2 routing and persistence semantics.
