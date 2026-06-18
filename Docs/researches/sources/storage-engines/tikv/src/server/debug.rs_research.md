# sources/storage-engines/tikv/src/server/debug.rs

## Purpose

`server/debug.rs` implements the classic raftstore debugger over shared RocksDB KV and raft engines. It exposes inspection, compaction, region metadata repair, MVCC repair, config modification, flashback, reset-to-version, and a small HTTP debug toggle for duplicate-key diagnostics. The code is operationally sensitive because several APIs intentionally rewrite raft metadata, raft logs, and MVCC column families.

The `Debugger` trait defined here is also implemented by `debug2.rs`, making this file the compatibility contract for debug tooling across raftstore generations.

## Important APIs, types, and functions

`Error` distinguishes invalid arguments, not-found states, boxed operational errors, engine-trait errors, and flashback failures. `RegionInfo` groups `RaftLocalState`, `RaftApplyState`, and `RegionLocalState`.

`BottommostLevelCompaction` converts HTTP/protobuf/debug options into RocksDB `DBBottommostLevelCompaction`.

`Debugger` declares the debug surface: raw gets, raft-log reads, region info and size, MVCC scanning, manual compaction, all-region listing, store identity, RocksDB stats, online config mutation, region property extraction, reset/flashback, statistics attachment, and range properties.

`DebuggerImpl<ER,E,L,K>` owns `Engines<RocksEngine, ER>`, optional Rocks statistics, `ResetToVersionManager`, `ConfigController`, and optional `Storage` for flashback. `InnerRocksEngineExtractor` permits raft DB access only when the raft engine is also a `RocksEngine`; generic raft engines reject direct raft DB reads.

Repair helpers include `set_region_tombstone`, `set_region_tombstone_by_id`, `recover_regions`, `recover_all`, `bad_regions`, `remove_failed_stores`, `drop_unapplied_raftlog`, and `recreate_region`. MVCC repair is implemented by `recover_mvcc_for_range` and `MvccChecker`.

`dump_default_cf_properties` and `dump_write_cf_properties` decode RocksDB range properties and MVCC user properties. `handle_dup_key_debug`, `handle_check`, and `handle_enable_debug` implement `/debug/dup-key/*` HTTP endpoints around `txn_types::ENABLE_DUP_KEY_DEBUG`.

## Control flow

Simple read APIs validate DB/CF combinations, select an engine, and read raw values or protobuf messages. `region_info` independently reads raft local state from the raft engine and apply/region state from KV CF_RAFT, returning not found only when all three are absent. `region_size` scans encoded region bounds in each requested CF and sums key/value bytes.

Manual compaction validates the DB/CF pair, resolves a column-family handle, builds `CompactOptions` with max subcompactions and bottommost-level choice, then calls RocksDB `compact_range_cf_opt`.

Tombstone-by-PD-region validates that local region state exists, the local peer belongs to this store, the target region has a higher conf version, and the target peers no longer include the same local peer. Only if all requested tombstones pass does the batched write sync to KV. Tombstone-by-id is more direct: it loads each local region state and marks it tombstone if present.

`remove_failed_stores` prevents removing the local store itself, scans selected or all region states, removes peers belonging to failed stores, optionally promotes a single remaining learner if no voters remain, preserves region epoch, and sync-writes updated region states.

`drop_unapplied_raftlog` loads region/apply/raft state, skips tombstones and already-applied regions, sets raft `last_index` and apply `commit_index` to `applied_index`, writes apply state to KV CF_RAFT, writes raft state through a raft log batch, garbage-collects raft entries `(applied_index + 1)..(last_index + 1)`, consumes the raft batch synchronously, and calls `kv.sync`.

`recreate_region` rejects invalid ranges and overlap with existing non-tombstone regions, then creates missing `RegionLocalState`, initial `RaftApplyState`, and initial `RaftLocalState` in synced KV and raft batches.

`MvccChecker` walks lock, default, and write CF iterators in key order. For each user key it deletes orphan or stale locks, orphan default records, and write records that require but lack a matching default record. `recover_mvcc_for_range` loops in write-batch chunks of 10240 fixes and can run read-only. `recover_all` divides the full data keyspace by approximate split keys and processes ranges on named threads.

Flashback first checks region flashback state against prepare/finish mode, builds a KV RPC context from region epoch and local peer, converts encoded keys back to raw keys, then calls prepare or finish flashback futures and maps response/region errors into `FlashbackFailed`.

## State and persistence behavior

This file directly reads and writes persistent TiKV state. KV CF_RAFT stores region local state and apply state; the raft engine stores raft local state and raft log entries; data CFs store MVCC lock/default/write records. Repair paths use synchronous write options or synchronous raft batch consumption for durability. `remove_failed_stores`, tombstoning, raft-log dropping, and region recreation are metadata mutations that can change restart behavior.

`reset_to_version` delegates persistent data rollback orchestration to `ResetToVersionManager`. Flashback executes through the storage layer and therefore participates in normal region/epoch checks. The duplicate-key debug flag is only an in-memory atomic.

## Dependencies and integration points

The debugger integrates with `engine_rocks`, `engine_traits`, `kvproto::debugpb/kvrpcpb/raft_serverpb`, `raftstore::store::PeerStorage`, raft `RawNode`, `ConfigController`, storage `Storage`, lock manager traits, `txn_types`, RocksDB range properties, hyper HTTP, and TiKV worker/thread utilities. It is used by debug services and administrative tooling, and it provides the trait that `debug2.rs` reuses for raftstore-v2.

## Risks and edge cases

The destructive helpers require strong operator correctness. Tombstoning by id bypasses the PD-region conf-version and scheduled-peer checks used by `set_region_tombstone`. `remove_failed_stores` intentionally leaves region epoch unchanged to avoid another class of inconsistency, but that also means metadata is manually divergent from PD until repaired. `drop_unapplied_raftlog` discards unapplied raft entries and must only be used when losing them is acceptable. `recreate_region` only checks local overlap and existing local metadata.

Several paths use `unwrap` after earlier assumptions (`region_local_state.unwrap`, storage existence for flashback, worker construction, iterator operations). `MvccChecker` has `unimplemented!` for shared locks returned by `txn_types::parse_lock`, so shared-lock data would panic. `divide_db(parts)` subtracts one from `parts`, so callers must avoid zero. Flashback unwraps store identity, region info, storage, and peer lookup before returning the async future.

## Test signals

Tests cover region overlap, DB/CF validation, raw get, raft log fetch, region info, region size, MVCC scan invalid inputs, tombstoning by PD region and by id, failed-store removal and learner promotion, dropping unapplied raft logs, bad-region detection through RawNode reconstruction, region recreation overlap checks, MVCC checker fix cases, raw scan boundaries, store identity, and manual compaction. The tests use temporary Rocks engines and mock storage/lock-manager types, so they are strong unit signals for local behavior but not full-cluster safety proofs.
