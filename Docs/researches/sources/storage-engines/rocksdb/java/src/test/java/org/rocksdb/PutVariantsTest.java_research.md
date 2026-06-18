## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutVariantsTest.java

### Purpose

`PutVariantsTest` parameterizes default-column-family `RocksDB.put` overloads and verifies each writes the intended key/value bytes.

### Important APIs, Types, And Functions

It uses `FunctionPut`, `RocksDB.put` byte-array overloads, `WriteOptions` overloads, offset/length overloads, direct and heap `ByteBuffer` overloads, and `MergeTest` byte helpers for little-endian longs.

### Control Flow

For each put function, the test opens a DB with `UInt64AddOperator` configured, writes long `100` under `"key"` through the parameterized function, reads the key, decodes the long, and asserts `100`.

### State And Persistence Behavior

The only persisted state is one key in the default CF. The merge operator is configured but not used by this test; it mainly provides a known binary value format shared with merge tests.

### Dependencies And Integration Points

This integrates Java overload dispatch, `WriteOptions`, offset/length JNI marshalling, and direct/heap ByteBuffer handling.

### Risks And Edge Cases

- Offset/length overloads must use only the intended slices of padded arrays.
- ByteBuffer overloads require correct flip/limit handling.
- Temporary write options in lambdas are not explicitly closed.

### Test Signals

Every overload must round-trip the binary long value `100`. Static research only; no test command was run.
