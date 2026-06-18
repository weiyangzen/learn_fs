# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBufferManager.java

## Purpose
`WriteBufferManager` wraps native RocksDB write buffer memory accounting and optional stalling. It lets DB instances bound memtable memory together with a block cache.

## Important APIs and Types
Constructors accept `bufferSizeBytes`, a `Cache`, and optional `allowStall`. `allowStall()` returns the Java-cached flag.

## Control Flow, State, and Persistence
Construction ensures the RocksDB native library is loaded, then creates the native write buffer manager with the cache handle. The only Java state is `allowStall_`; memory usage is native and runtime-only. Disposal releases the native manager.

## Dependencies and Integration Points
Depends on `RocksObject`, `Cache`, `RocksDB.loadLibrary`, and JNI. It integrates with DB/table options that accept a write buffer manager and with cache-backed memory budgets.

## Risks and Test Signals
The cache handle must remain valid for native manager creation/use. `allowStall=true` changes write latency behavior under memory pressure. This subset has no direct write buffer manager tests.
