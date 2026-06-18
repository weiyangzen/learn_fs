# sources/storage-engines/rocksdb/include/rocksdb/snapshot.h

Purpose: This header declares RocksDB's immutable snapshot handle and a small RAII wrapper for acquiring/releasing snapshots. Snapshots provide stable point-in-time read views for `ReadOptions::snapshot`.

Important APIs and types: `Snapshot` is an abstract class with `GetSequenceNumber()`, `GetUnixTime()`, and `GetTimestamp()`. Its destructor is protected so users release snapshots through DB APIs. `ManagedSnapshot` constructs by acquiring `DB::GetSnapshot()` or by taking ownership of an existing snapshot pointer, releases it in the destructor, and exposes `snapshot()`.

Control flow: Applications call `DB::GetSnapshot()` and pass the pointer into read options. `ManagedSnapshot` wraps that lifecycle: constructor stores the DB and snapshot, destructor calls release, and `snapshot()` returns the managed pointer.

State and persistence behavior: A snapshot pins an in-memory version/sequence view and can keep old memtable/SST resources alive until release. It is immutable and thread-safe to read. Snapshot handles are not persisted across process restarts; sequence number and timestamps reflect DB state at creation.

Dependencies and integration points: It depends on `rocksdb/types.h` for `SequenceNumber` and forward-declares `DB`. Read paths, iterators, transactions, compaction garbage collection, and resource cleanup all integrate with snapshot lifetime.

Risks and edge cases: Failing to release snapshots can retain obsolete files and block cleanup/compaction. A snapshot must be released to the same DB that created it. `ReadOptions::snapshot` must not outlive the snapshot. `ManagedSnapshot` is simple ownership; users should avoid double-release when passing an already-owned snapshot.

Test signals: Tests should cover sequence/timestamp visibility, RAII release, multi-threaded reads through one snapshot, resource pinning until release, and invalid/double ownership misuse in debug or sanitizer builds.
