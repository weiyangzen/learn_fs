# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/VectorMemTableConfig.java

## Purpose
`VectorMemTableConfig` configures RocksDB's vector memtable representation from Java. It extends `MemTableConfig` and supplies a native memtable factory handle.

## Important APIs and Types
`DEFAULT_RESERVED_SIZE` is zero. `setReservedSize(int)` stores the initial vector capacity and returns `this`; `reservedSize()` returns it. `newMemTableFactoryHandle()` passes the size to native code.

## Control Flow, State, and Persistence
Unlike many wrapper files, this class keeps Java state in `reservedSize_` until a native factory is requested. Native creation can throw `IllegalArgumentException`. Once the factory is installed in options, memtable behavior is native and affects in-memory write buffering, not directly persistent file format.

## Dependencies and Integration Points
It depends on `MemTableConfig` and native `newMemTableFactoryHandle`. It integrates with options APIs that accept memtable config objects.

## Risks and Test Signals
Invalid or extreme reserved sizes can produce native argument errors or memory pressure. There are no direct tests for vector memtables in this subset.
