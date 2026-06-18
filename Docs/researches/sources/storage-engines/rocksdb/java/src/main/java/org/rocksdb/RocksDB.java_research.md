# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksDB.java

## Purpose
`RocksDB` is the primary Java facade for a native RocksDB database. It models a persistent ordered key/value map and exposes JNI-backed operations for opening databases, managing column families, reading and writing data, creating iterators and snapshots, querying properties, compacting data, flushing WAL/memtables, ingesting external SST files, tracing, secondary-instance catch-up, and destruction. The class extends `RocksObject`, so it owns an immutable native DB pointer until closed.

## Important APIs and Types
- Constants: `DEFAULT_COLUMN_FAMILY`, `NOT_FOUND`, and internal direct/heap ByteBuffer error text.
- Library lifecycle: `loadLibrary()`, `loadLibrary(List<String>)`, `rocksdbVersion()`, and nested `Version`.
- Open variants: default read-write, column-family read-write, read-only, read-only with WAL checking, and secondary open variants.
- Resource lifecycle: `closeE()`, `close()`, `isClosed()`, `disposeInternal(long)`, `makeDefaultColumnFamilyHandle()`.
- Column family APIs: `listColumnFamilies`, create/bulk-create/import, drop/bulk-drop, and `destroyColumnFamilyHandle`.
- Data APIs: overloaded `put`, `delete`, `singleDelete`, `deleteRange`, `merge`, `write`, `get`, `multiGetAsList`, `multiGetByteBuffers`, `keyExists`, and `keyMayExist`.
- Navigation APIs: `newIterator`, `newIterators`, `getSnapshot`, and `releaseSnapshot`.
- Admin/metadata APIs: `getProperty`, `getMapProperty`, long properties, approximate sizes, memtable stats, compaction methods, mutable option setters/getters, performance context, background-work controls, level metrics, `getName`, `getEnv`, flush/WAL methods, live files, WAL files, updates since, metadata, table properties, checksum, tracing, and `destroyDB`.
- Helper types: nested `CountAndSize`, nested `LiveFiles`, and nested `Version`.

## Control Flow
Library loading is guarded by an `AtomicReference<LibraryState>`. The winning thread transitions `NOT_LOADED -> LOADING`, loads optional compression libraries, loads `rocksdbjni`, initializes the static encoded native version, and publishes `LOADED`. Competing threads wait with a 10-second timeout and preserve interruption if interrupted.

Open methods normalize Java descriptors into `byte[][]` names and `long[]` option handles before invoking native open calls. Column-family opens require that the default column family is included. Returned native handles are converted into a `RocksDB` plus Java `ColumnFamilyHandle` wrappers, and owned handles are tracked in `ownedColumnFamilyHandles` so DB close can dispose them.

Most read/write overloads are thin normalization layers. They validate byte-array ranges with `CheckBounds` or local `checkBounds`, select default versus explicit column-family handles, select default versus explicit read/write options, and forward to native methods. ByteBuffer paths distinguish direct buffers from heap-backed buffers; mixed direct/indirect key/value pairs throw `RocksDBException`, and successful operations advance positions or adjust limits according to API contracts.

`closeE()` and `close()` first close tracked column-family handles, clear the list, then atomically flip inherited ownership and close the native database. `closeE()` propagates `RocksDBException`; `close()` suppresses it. Both call `disposeInternal()` in a finally path after native close.

## State and Persistence Behavior
Persistent state lives in the native RocksDB database files at the path passed to open. Java state mainly preserves native handles, default read options, an options reference to prevent premature GC, the default column-family handle, and a list of owned column-family handles. Writes, deletes, merges, flushes, WAL sync, compactions, file deletions, and external file ingestion mutate native persistent state. Snapshots expose stable sequence-numbered views but are released by the DB, not by the `Snapshot` object itself. `getLiveFiles`, `getSortedWalFiles`, `getUpdatesSince`, and metadata APIs expose persistence surfaces used by backup, replication, and inspection code.

## Dependencies and Integration Points
The class depends on a large set of RocksJNI wrappers: `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `ReadOptions`, `WriteOptions`, `WriteBatch`, `WriteBatchWithIndex`, `Range`, `Slice`, `Status`, `ByteBufferGetStatus`, `KeyMayExist`, `PerfLevel`, `PerfContext`, `FlushOptions`, metadata classes, trace writers, and many option classes. It integrates with native code through an extensive private native method table, with `NativeLibraryLoader` and `Environment` for library loading, and with Java collections and `ByteBuffer` for data movement.

## Risks
- Native handle ownership is central. Closing a DB before closing dependent iterators, snapshots, options, or column-family handles can produce native misuse.
- Several ByteBuffer methods rely on assertions for directness/null checks, so production JVMs with assertions disabled may pass bad buffers into JNI unless native code defends itself.
- `singleDelete` is explicitly experimental and has strict write-history preconditions; misuse can produce undefined data behavior.
- Multi-key APIs protect some size mismatches to avoid segmentation faults; any new overload must preserve those checks.
- `get` returning `NOT_FOUND` and possible native negative statuses is documented as an API wart.
- `getLiveFiles(boolean)` returns null if native returns null and encodes manifest size in the final string, so callers and native changes must preserve that convention.
- `startTrace` transfers trace-writer ownership to C++; missing the `disOwnNativeHandle()` pattern would double free.

## Test Signals
Strong tests would cover concurrent `loadLibrary`, all open variants including missing default CF rejection, close idempotence, column-family ownership cleanup, byte-array range validation, direct/heap ByteBuffer behavior and position/limit changes, multi-get size mismatch errors, `keyMayExist` holder encodings, snapshot release behavior, live-file parsing, mutable option round trips, and JNI exception propagation. Integration tests need real RocksDB instances to validate persistence, WAL/flush behavior, compaction/file metadata, secondary catch-up, and external SST ingestion.
