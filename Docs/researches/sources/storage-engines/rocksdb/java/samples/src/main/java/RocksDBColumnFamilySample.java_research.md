# sources/storage-engines/rocksdb/java/samples/src/main/java/RocksDBColumnFamilySample.java

## Purpose
This sample demonstrates Java column-family creation, reopening a DB with multiple column families, writing to specific column families, atomic batch writes across column families, and dropping a column family.

## Important APIs, Types, and Functions
The class uses `RocksDB.loadLibrary`, `Options`, `RocksDB.open`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, `DBOptions`, `WriteBatch`, and `WriteOptions`. The only entry point is `main`.

## Control Flow
The program expects a database path argument. It first opens a DB with `createIfMissing`, creates `new_cf`, and closes. It then builds descriptors for the default column family and `new_cf`, opens both, writes a key to the non-default family, creates a `WriteBatch` containing writes to both column families and a delete in `new_cf`, writes the batch atomically, drops `new_cf`, and finally closes all column family handles.

## State and Persistence Behavior
The sample creates persistent column-family metadata and key/value data under the provided path. It demonstrates that non-default column families must be listed when reopening and that column-family handles require explicit close.

## Dependencies and Integration Points
It exercises public Java DB and write-batch APIs, which route through JNI bridge files including RocksDB open code and `write_batch.cc`.

## Risks and Edge Cases
Assertions depend on JVM assertion settings. The sample creates `ColumnFamilyOptions` inside descriptors without explicit closing, which may be acceptable for a sample but is a lifecycle signal. The DB path argument is user-controlled and the sample drops the created column family.

## Test Signals
Useful checks include verifying column-family descriptor ordering, write-batch atomicity across column families, proper handle closure in finally, and drop-column-family behavior after writes.
