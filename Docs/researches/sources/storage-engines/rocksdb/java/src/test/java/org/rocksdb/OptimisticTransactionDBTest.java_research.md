## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionDBTest.java

### Purpose

`OptimisticTransactionDBTest` validates opening, column-family handling, transaction creation, base DB access, and iterator behavior for `OptimisticTransactionDB`.

### Important APIs, Types, And Functions

It uses `OptimisticTransactionDB.open` overloads, `beginTransaction`, `OptimisticTransactionOptions`, `WriteOptions`, `getBaseDB`, `isOwningHandle`, `newIterator`, `ColumnFamilyDescriptor`, and `ColumnFamilyHandle`.

### Control Flow

Tests open an optimistic transaction DB with simple options, open with default plus custom CF descriptors, assert missing default CF descriptors are rejected, create transactions with and without `OptimisticTransactionOptions`, verify `getBaseDB` returns a non-owning base `RocksDB` wrapper, and write/iterate a simple key/value pair.

### State And Persistence Behavior

Temporary DB state includes CF metadata and a single iterator-visible key. `getBaseDB` ownership assertions protect native handle ownership so closing the wrapper does not double-close the optimistic DB.

### Dependencies And Integration Points

This integrates optimistic transaction DB wrappers with base RocksDB APIs, CF descriptor validation, transaction options, write options, and iterator creation.

### Risks And Edge Cases

- Column-family open requires default CF presence; missing it must fail before native misuse.
- Non-owning base DB wrapper lifetime is subtle and must be tied to the owning optimistic transaction DB.
- Column-family handles are manually closed and must not outlive the DB.

### Test Signals

Signals are non-null DB/transaction/iterator objects, expected `IllegalArgumentException`, non-owning base DB handle, and exact iterator key/value. Static research only; no test command was run.
