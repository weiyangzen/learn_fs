# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabase.java

## Purpose

`RocksDatabase` is the central managed wrapper around `org.rocksdb.RocksDB`. It opens DBs with column families, wraps native resources in managed classes, tracks concurrent operations, closes on severe RocksDB errors, and exposes lower-level operations used by `RDBTable`, checkpointing, compaction, WAL update streaming, and SST maintenance. The complete 916-line source was read for this report.

## Important APIs, Types, and Functions

Important public/package APIs include `open`, `listColumnFamiliesEmptyOptions`, `getColumnFamily`, `dropColumnFamily`, `put`, `get`, `keyMayExist`, `delete`, `deleteRange`, `batchWrite`, `newIterator`, `flush`, `flushWal`, `compactRange`, `compactDB`, `createCheckpoint`, `getUpdatesSince`, `getLatestSequenceNumber`, `estimateNumKeys`, `getProperty`, `ingestExternalFile`, `deleteFilesNotMatchingPrefix`, `getManagedRocksDb`, and `close`. Nested types are `RocksCheckpoint` and `ColumnFamily`.

## Control Flow

`open` discovers extra existing column families not present in the requested family set, builds descriptors, opens read-only or read-write RocksDB, and wraps returned handles. Every operation first calls `acquire()`, incrementing a shared counter unless close has begun. Iterators receive an acquire token that is released when the managed iterator closes. On `RocksDBException`, `closeOnError` asynchronously closes the DB for corruption and IO errors. `close()` marks the DB closed, cancels background work, closes listeners, waits for the active-operation counter to drain, then closes handles, DB, descriptors, write options, and DB options.

## State and Persistence Behavior

The class owns persistent RocksDB state at the DB path and native resources for DB options, write options, descriptors, column family handles, and the DB instance. Data mutation methods persist to RocksDB or WAL according to configured write options. `RocksCheckpoint.createCheckpoint` materializes a filesystem checkpoint. `dropColumnFamily` removes a column family from RocksDB and local maps. `deleteFilesNotMatchingPrefix` deletes eligible last-level SST files whose key ranges do not match a configured prefix.

## Dependencies and Integration Points

It integrates RocksJava through HDDS managed wrappers (`ManagedRocksDB`, `ManagedReadOptions`, `ManagedWriteBatch`, `ManagedCheckpoint`, and related option classes), `TableConfig`, `RDBTable`, external file ingestion, `RocksDiffUtils`, and Ratis `MemoizedSupplier`/`UncheckedAutoCloseable`. It is the foundation for all RocksDB-backed metadata tables.

## Risks and Edge Cases

The acquire counter is critical: leaked iterators or long operations can delay close indefinitely. Column families discovered from old or future versions are opened as extras, which supports compatibility but can hide schema drift. `deleteFilesNotMatchingPrefix` assumes SST level constraints and prefix range logic are correct before deleting files. `getLastLevel()` assumes there is at least one live file. `finalize()` only warns on leaks and should not be relied on. ByteBuffer logging uses decoded keys and can be expensive or lossy for non-string keys.

## Test Signals

High-value tests include open with declared and extra column families, read-only open, corruption/IO close-on-error behavior, iterator-held close blocking and release, batch writes, ByteBuffer get sizing, keyMayExist enum handling, checkpoint creation, flush/compact paths, drop column family cleanup, and prefix-based SST deletion with synthetic metadata.
