# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Snapshot.java

## Purpose
`Snapshot` wraps a native RocksDB snapshot handle, representing a stable database sequence view for reads and iterators.

## Important APIs and Types
- Extends `RocksObject`.
- Package-private constructor accepts a native snapshot handle and immediately disowns it.
- `getSequenceNumber()` returns the snapshot sequence number.
- `disposeInternal(long)` intentionally does nothing.

## Control Flow
`RocksDB.getSnapshot()` creates `Snapshot` when native returns a non-zero handle. The constructor calls `disOwnNativeHandle()` because the DB, not the Java snapshot, releases the native snapshot. `RocksDB.releaseSnapshot(snapshot)` is the actual release path.

## State and Persistence Behavior
The snapshot handle points to native DB state pinned at a sequence number. It does not own persistent data, but it can keep older data versions/files alive until released by the DB. Java close of `Snapshot` does not release the native snapshot.

## Dependencies and Integration Points
It depends on `RocksObject` and JNI. It integrates with `ReadOptions`/iterator refresh flows that read under a snapshot and with `RocksDB.releaseSnapshot`.

## Risks
The no-op `disposeInternal` means forgetting to call `RocksDB.releaseSnapshot` leaks native snapshot state even if the Java object is closed/GC'd. Using a snapshot after release is forbidden by `RocksDB.releaseSnapshot` documentation. DB lifetime must dominate snapshot use.

## Test Signals
Tests should verify sequence number retrieval, disowned close no-op behavior, release through DB, repeated release/null behavior at DB API level, and resource retention/release effects on file cleanup where practical.
