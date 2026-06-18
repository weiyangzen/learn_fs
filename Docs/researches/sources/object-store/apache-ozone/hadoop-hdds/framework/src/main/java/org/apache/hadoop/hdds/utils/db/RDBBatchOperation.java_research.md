# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBBatchOperation.java

## Purpose
`RDBBatchOperation` is the RocksDB `BatchOperation` implementation. It collects put/delete operations by column family, deduplicates operations on the same key, then applies the final operations to a managed RocksDB write batch for atomic commit.

## Important APIs and Types
Factories `newAtomicOperation()` and `newAtomicOperation(ManagedWriteBatch)` create batches. Public operations include `put`, `delete`, `commit(RocksDatabase)`, `commit(RocksDatabase, ManagedWriteOptions)`, and `close`. Internal `Bytes` wraps heap or direct key data with content equality. Internal `Op`, `SingleKeyOp`, `PutOp`, `DeleteOp`, and `OpCache` manage lifecycle and deduplication.

## Control Flow and State
`OpCache` groups operations by column-family name. Adding a new op removes and closes any previous op for the same key, tracks discarded size/count, and stores the latest op. Commit prepares each family cache once, applies ops to the write batch, writes the batch to RocksDB, and clears temporary resources through try-with-resources. Closing closes the write batch and any cached operations.

## Persistence, Dependencies, and Integration
Persistence occurs only on commit via `RocksDatabase.batchWrite`. The class depends on managed write batches, managed direct/heap slices, `CodecBufferCodec`, `ColumnFamily`, `ManagedWriteOptions`, and HDDS `IOUtils`. It is created and committed by `RDBStore`.

## Risks and Test Signals
The class is explicitly not thread-safe and is single-use after commit. Deduplication relies on stable byte content and proper closure of slices/buffers. `delete(byte[])` and `put(byte[], byte[])` allocate direct codec buffers. Tests should cover overwrite deduplication, delete-after-put, put-after-delete, multi-CF batches, commit once, close without commit warning/discard, direct and heap key equality, write options commit, and resource closure on exceptions.
