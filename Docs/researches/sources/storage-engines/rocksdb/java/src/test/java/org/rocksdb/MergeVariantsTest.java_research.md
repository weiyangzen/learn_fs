## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeVariantsTest.java

### Purpose

`MergeVariantsTest` parameterizes equivalent Java `RocksDB.merge` overloads and verifies each overload writes the same merge operand to RocksDB.

### Important APIs, Types, And Functions

The central type is the `FunctionMerge<RocksDB, byte[], byte[]>` functional interface. Parameters cover plain byte-array `merge`, `WriteOptions` overloads, offset/length byte-array overloads, direct `ByteBuffer`, and heap `ByteBuffer` overloads. It reuses `MergeTest.longToByteArray` and `longFromByteArray` with `UInt64AddOperator`.

### Control Flow

JUnit `Parameterized` creates one test instance per merge function. The test opens a temporary DB with `UInt64AddOperator`, writes `100` under `"key"`, invokes the parameterized merge to add `1`, then reads and verifies `101`.

### State And Persistence Behavior

The state under test is one persisted key whose value is transformed by RocksDB's native merge machinery. Sliced byte-array overloads allocate larger arrays with prefixes/suffixes, checking JNI respects offsets and lengths rather than consuming the full backing arrays.

### Dependencies And Integration Points

This integrates RocksDB Java overload dispatch, `WriteOptions`, heap/direct `ByteBuffer` handling, UTF-8 string construction for padded arrays, and the native `UInt64AddOperator`.

### Risks And Edge Cases

- Direct and heap buffers must be flipped correctly so position/limit are honored.
- Offset/length overloads can corrupt keys or values if JNI uses backing array bounds incorrectly.
- Temporary `WriteOptions` created inside lambdas are not explicitly closed, so the test favors API coverage over strict resource accounting.

### Test Signals

All merge overloads must return `101` from the same key. Static research only; no test command was run.
