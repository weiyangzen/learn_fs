## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutCFVariantsTest.java

### Purpose

`PutCFVariantsTest` parameterizes `RocksDB.put` overloads that target explicit column-family handles and verifies each variant writes readable bytes.

### Important APIs, Types, And Functions

It uses the `FunctionCFPut` functional interface, CF `put` overloads with and without `WriteOptions`, offset/length byte arrays, direct and heap `ByteBuffer`, `DBOptions`, `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, and the `UInt64AddOperator` byte helpers from `MergeTest`.

### Control Flow

For each put overload, the test opens a DB with default and `"new_cf"` column families, writes little-endian `100` to `"cfkey"` in the non-default CF through the parameterized function, reads it back, creates a third CF, writes `200` through the normal CF put API, reads it, and asserts both values.

### State And Persistence Behavior

State is temporary DB data in non-default and dynamically created column families. The test verifies writes reach the intended CF and are not routed to default.

### Dependencies And Integration Points

It integrates parameterized JUnit, Java NIO buffers, offset/length JNI marshalling, column-family handles, and merge-operator-configured CF options.

### Risks And Edge Cases

- Offset/length overloads must ignore array padding.
- Heap/direct `ByteBuffer` position and limit handling must be exact.
- Temporary `WriteOptions` inside lambdas are not explicitly closed.

### Test Signals

All overloads must produce `100` in `"new_cf"` and `200` in the dynamically created CF. Static research only; no test command was run.
