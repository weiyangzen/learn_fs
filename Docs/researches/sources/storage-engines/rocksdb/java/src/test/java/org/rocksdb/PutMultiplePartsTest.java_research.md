## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutMultiplePartsTest.java

### Purpose

`PutMultiplePartsTest` validates transaction APIs that accept multipart keys and values as `byte[][]`, concatenating the parts into one logical key and value.

### Important APIs, Types, And Functions

It uses `TransactionDB`, `Transaction.put`, `Transaction.putUntracked`, CF overloads of both methods, `syncWal`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, and helper methods `generateItems`, `generateItemsAsList`, `validateResults`, and `validateResultsCF`.

### Control Flow

Parameterized tests run with 2, 3, 250, and 20,000 parts. Each test opens a transaction DB, begins a transaction, generates key parts like `key0:`, `key1:`, and value parts like `value0`, `value1`, calls tracked or untracked multipart put with or without CF handle, commits, syncs WAL, closes, then reopens a normal DB and reads the concatenated key.

### State And Persistence Behavior

The transaction writes one logical key/value assembled by native RocksDB from many Java byte arrays. `syncWal` reinforces durability before validation after close/reopen.

### Dependencies And Integration Points

This integrates transaction DB, tracked/untracked write paths, CF routing, Java array-of-array marshalling, WAL sync, and reopen validation.

### Risks And Edge Cases

- Very large part counts stress JNI loops and native `SliceParts` construction.
- Key and value part counts must match; this test does not cover mismatch errors.
- CF validation reopens descriptors in non-standard order (`cfTest`, `default`) and relies on handle index 0 for `cfTest`.

### Test Signals

The read value for the concatenated key must equal the concatenation of all value parts for default and CF variants. Static research only; no test command was run.
