# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileWriter.java

## Purpose
`SstFileWriter` wraps native external SST creation. It lets Java callers build an SST file with sequence number zero that can later be ingested into a RocksDB instance.

## Important APIs and Types
Construction takes `EnvOptions` and `Options`. Public methods include `open(String)`, overloaded `put` for `Slice`, `DirectSlice`, `ByteBuffer`, and `byte[]`, overloaded `merge`, overloaded `delete`, `finish()`, and `fileSize()`.

## Control Flow
The constructor allocates a native writer. `open` starts output to a file path. Mutating calls delegate to native writer operations. Direct `ByteBuffer` `put` asserts both buffers are direct, passes position/remaining to native code, then advances both positions to their limits. `finish` closes/finalizes the SST. `fileSize` reports native writer size.

## State and Persistence Behavior
The object owns a native writer handle. State transitions are native: allocated, opened, receiving sorted records, and finished. The class writes persistent SST data to the filesystem via the native writer but stores no Java-side record data.

## Dependencies and Integration Points
It extends `RocksObject`, depends on `EnvOptions`, `Options`, `Slice`, `DirectSlice`, `ByteBuffer`, and `RocksDBException`, and integrates with external file ingestion workflows elsewhere in RocksJava.

## Risks and Test Signals
Tests should check sorted-key requirements, duplicate keys, merge/delete records, file-size updates, missing `finish`, invalid file paths, and ingestion compatibility. The `ByteBuffer` `put` path relies on Java assertions for directness, so with assertions disabled an invalid buffer can reach JNI; tests should cover invalid buffer handling at native boundaries.
