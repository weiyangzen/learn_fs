<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/engine.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/engine.rs

## Purpose
`engine.rs` implements the core `engine_traits` read/write surface for the tirocks-backed `RocksEngine`: existence checks, CF lookup, snapshots, iterators, point reads, and synchronous mutations.

## Important APIs, Types, and Functions
`RocksEngine` stores `Arc<Db>` and a cached `multi_batch_write` flag. `new`, `exists`, `as_inner`, `cf`, `snapshot`, `multi_batch_write`, and test-only `flush` are helper APIs. `approximate_memtable_stats` forwards tirocks approximate memtable stats.

Trait implementations cover `Iterable`, `Peekable`, and `SyncMutable`. Point reads use a private `get` helper that builds tirocks `ReadOptions`, applies `fill_cache`, and fills `RocksPinSlice` with `get_pinned`.

## Control Flow
`exists` checks for a directory and `CURRENT` file; non-empty directories without `CURRENT` return corruption. Iteration converts `IterOptions` through `engine_iterator::to_tirocks_opt`, resolves the CF handle, and constructs a tirocks iterator. Mutations resolve the default or named CF handle and call tirocks `put`, `delete`, or `delete_range` with default write options.

## State and Persistence Behavior
Synchronous mutation methods persist writes/deletes/range deletes through tirocks. Snapshots pin read state. `exists` is read-only but classifies ambiguous non-empty directories as corruption.

## Dependencies and Integration Points
It depends on tirocks `Db`, `RawCfHandle`, `ReadOptions`, `WriteOptions`, iterator/snapshot wrappers, `RocksPinSlice`, status conversion, and `engine_traits`. Tests use utility DB construction and protobuf message helpers from engine traits.

## Risks and Edge Cases
The implementation is partial; many engine traits live in other modules or are not present in this subset. Point reads set only `fill_cache`, not all read options. `fs::read_dir(...).unwrap()` can panic on permission errors. All writes use default write options; there is no explicit sync/WAL option handling here. The cached multi-batch flag assumes DB options do not change after construction.

## Test Signals
Tests cover message put/get on engine and snapshot, CF point reads and missing CF errors, forward scans, seek behavior, scan early stop, and snapshot isolation after later writes. Further coverage should include delete/range delete, write option behavior, existence corruption cases, and concurrent snapshots.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/engine.rs -->
