# sources/storage-engines/tikv/components/engine_tirocks/src/snapshot.rs

Purpose: Implements the engine-trait `Snapshot`, `Iterable`, and `Peekable` APIs on top of TiRocks snapshots.

Important APIs and control flow: `RocksSnapshot` stores an `Arc<Snapshot<'static, Arc<Db>>>`. `new` captures a DB snapshot. Internal `get` builds TiRocks `ReadOptions`, applies `fill_cache`, calls `get_pinned`, and maps found/not-found/status into `Result<Option<RocksPinSlice>>`. `iterator_opt` converts engine-trait iterator options, resolves the CF handle, and creates a `RocksSnapIterator`.

State, persistence, and dependencies: Snapshot state is a shared pinned TiRocks snapshot view of the DB at creation time; reads do not persist new data. It depends on local iterator option conversion, CF handle resolution, pinned slices, and status conversion.

Integration points, risks, and test signals: Used by TiKV read paths needing a stable view while writes continue. Risks include lifetime erasure around `'static`, stale CF handles if a CF is dropped, pinned-slice ownership, and option gaps because only `fill_cache` is mapped for point reads. Shared snapshot tests verify point reads, CF reads, and read consistency after later puts/deletes.
