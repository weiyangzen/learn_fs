# sources/storage-engines/tikv/src/storage/mvcc/consistency_check.rs

## Purpose

This file implements MVCC-aware raftstore consistency checking and reusable MVCC info scanning over TiKV's three MVCC column families. It serves two related purposes: `Mvcc<E>` is a raftstore `ConsistencyCheckObserver` that computes a CRC32 hash over live MVCC state plus region state, and `MvccInfoScanner`/`MvccInfoIterator` expose structured MVCC information for debugging or RPC-style inspection.

## Important APIs, Types, and Functions

- `Mvcc<E: KvEngine>` is the consistency-check coprocessor. It carries an `Arc<AtomicU64>` local GC safe point and has no engine instance of its own, only `PhantomData<E>`.
- `get_safe_point_for_check` widens the loaded safe point by `SAFE_POINT_WINDOW` seconds after shifting through TiKV's physical timestamp bits. The leader embeds this adjusted safe point into the consistency-check context.
- `ConsistencyCheckObserver::update_context` appends the MVCC check method byte and little-endian safe point to raftstore's context buffer, then returns `true` to skip later observers.
- `ConsistencyCheckObserver::compute_hash` validates the method byte, reads the safe point, skips stale or zero-window checks, scans MVCC data from region start/end data keys, and folds the raft region-state key/value into the checksum.
- `MvccInfoObserver` is the scanner callback contract. It receives `on_new_item`, per-CF callbacks for write/lock/default entries, and an `emit` hook for a completed user key.
- `MvccInfoScanner<Iter, Ob>` merges the write, lock, and default CF iterator streams by user-key prefix and delegates parsing/selection to an observer.
- `MvccInfoCollector` builds `kvproto::kvrpcpb::MvccInfo` values with writes, lock, and default values converted into protobuf MVCC records.
- `MvccInfoIterator` wraps the scanner as a bounded Rust iterator.
- `MvccChecksum` hashes non-stale writes, locks, and only default values that correspond to committed writes after the safe point.

## Control Flow

`update_context` serializes a method discriminator and adjusted safe point. Followers call `compute_hash`, which rejects empty context, checks stale local safe-point conditions, creates three CF iterators over the data-key range, and repeatedly calls `MvccInfoScanner::next_item` until exhausted. The scanner chooses the next user-key prefix by comparing the lock key with the timestamp-truncated write key. It then drains all writes for that prefix, all matching lock records, and all matching default records, stopping each CF loop when the observer returns `false` because the iterator has reached another user key.

For checksums, `on_write` skips records whose commit timestamp is at or below the safe point, hashes newer write records, and records their start timestamps. `on_default` sorts the collected start timestamps lazily and hashes a default CF value only when its start timestamp belongs to a committed write newer than the safe point. This prevents uncommitted default values from affecting consistency hashes.

## State and Persistence Behavior

The code is read-only with respect to RocksDB. It reads `CF_WRITE`, `CF_LOCK`, `CF_DEFAULT`, and `CF_RAFT` snapshots, and uses the local safe point atomically with acquire ordering. Persistent MVCC state remains in the engine; transient scanner state includes iterator positions, current user key, collected protobuf info, checksum digest, and per-key committed start timestamps.

## Dependencies and Integration Points

The observer plugs into `raftstore::coprocessor::ConsistencyCheckObserver`. It depends on `engine_traits` iterators and CF constants, `keys::*` data/region key encoding, `txn_types::Key`, `WriteRef`, `parse_lock`, TiKV's `Either`, and kvproto MVCC protobuf structures. The public re-exports in `mvcc/mod.rs` expose `MvccConsistencyCheckObserver`, `MvccInfoScanner`, `MvccInfoCollector`, and `MvccInfoIterator` to the rest of storage.

## Risks and Edge Cases

- `update_context` uses `unsafe set_len` plus pointer copy. The length reservation and copy size are straightforward, but changes here require care.
- Shared locks parsed by `txn_types::parse_lock` are explicitly `unimplemented!` in collector and checksum paths. If shared-lock encoding can appear in these code paths, consistency checks or debug scans may panic.
- Safe-point logic intentionally skips checks when the embedded safe point is stale relative to the local safe point; this avoids false mismatches but can reduce coverage during fast GC movement.
- Iterator bounds reject non-MVCC data keys except `DATA_MAX_KEY`; callers must pass data-key encoded region boundaries.
- `MvccChecksum` depends on write/default ordering per key and hashes default values only after seeing writes for that item.

## Test Signals

Tests cover context serialization and 120-second safe-point adjustment, checksum stability when safe points move within a stale range and difference when old committed data becomes included, and `MvccInfoCollector` behavior across default, lock, and write CF records. Test fixtures use `TestEngineBuilder`, transaction helpers, and explicit CF writes.
