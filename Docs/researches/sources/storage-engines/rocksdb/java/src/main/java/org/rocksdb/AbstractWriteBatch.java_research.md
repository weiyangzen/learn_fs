# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractWriteBatch.java

- **Purpose:** Shared implementation of `WriteBatchInterface` operations for native write batch wrappers and subclasses.
- **Important APIs/types/functions:** Extends `RocksObject`; implements `count`, `put`, `merge`, `delete`, `singleDelete`, `deleteRange`, `putLogData`, `clear`, `setSavePoint`, `rollbackToSavePoint`, `popSavePoint`, `setMaxBytes`, and `getWriteBatch`. Abstract hooks map each operation to native methods with explicit handle/length/cf-handle parameters.
- **Control flow:** Public byte-array methods pass arrays with their lengths. Column-family overloads append the `ColumnFamilyHandle.nativeHandle_`. Direct `ByteBuffer` put/delete methods pass current position and remaining bytes, then advance positions to limits. Savepoint and rollback operations delegate to native stack behavior.
- **State and persistence behavior:** Batch state is native and represents pending write operations, savepoints, log data, and max-byte constraints. Persistence occurs only when a database writes the batch; this class does not itself write to disk.
- **Dependencies:** Depends on `RocksObject`, `WriteBatchInterface`, `ColumnFamilyHandle`, `WriteBatch`, `RocksDBException`, and `ByteBuffer`.
- **Integration points:** Base for `WriteBatch`, `WriteBatchWithIndex`, transaction write batch access, WAL filters, and database write APIs.
- **Risks:** Direct ByteBuffer `put` uses assertions to require direct buffers; with assertions disabled, invalid buffers can reach JNI. Byte-array methods do not null-check. Borrowed write batches returned by callbacks require careful ownership. Column-family handles must outlive operations.
- **Test signals:** All operation overloads, direct-buffer position advancement, savepoint rollback/pop errors, count tracking, max byte enforcement, column-family writes, and exception propagation from native write batch operations.
