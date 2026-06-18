## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeTest.java

### Purpose

`MergeTest` validates Java bindings for RocksDB merge operators. It covers merge operators set by registered name, merge operators set by Java wrapper instance, column-family-specific merge options, native object lifetime/reuse, string-append delimiter behavior, and invalid merge-operator-name inputs.

### Important APIs, Types, And Functions

Important APIs are `Options.setMergeOperatorName`, `ColumnFamilyOptions.setMergeOperatorName`, `Options.setMergeOperator`, `ColumnFamilyOptions.setMergeOperator`, `StringAppendOperator`, `UInt64AddOperator`, `RocksDB.merge`, `RocksDB.put`, `RocksDB.get`, `RocksDB.open`, `DBOptions`, `ColumnFamilyDescriptor`, and `ColumnFamilyHandle`. The helper methods `longToByteArray` and `longFromByteArray` encode/decode little-endian 64-bit values expected by the `uint64add` merge operator.

### Control Flow

Each test opens a temporary database, installs a merge operator, writes a base value, performs one merge, and asserts the resolved value. Column-family tests open or create additional CFs and close every handle in `finally`. GC behavior tests intentionally open and close DBs while reusing, replacing, or freshly constructing operator objects to ensure Java objects keep native merge-operator handles alive long enough.

### State And Persistence Behavior

The database state is temporary JUnit state under `TemporaryFolder`, but operations exercise durable RocksDB writes, merge operands, column-family metadata, and reopen behavior. Merge resolution is verified through `get`, so failures can indicate option propagation, native merge function lookup, byte order, or JNI lifetime issues.

### Dependencies And Integration Points

This test depends on the native RocksDB library resource, AssertJ, JUnit, Java `ByteBuffer`, `StringAppendOperator`, `UInt64AddOperator`, and column-family open/create APIs. It integrates with registered C++ merge operator names (`stringappend`, `uint64add`) and Java-owned native operator wrappers.

### Risks And Edge Cases

- `cFStringOption` uses `RocksDB.DEFAULT_COLUMN_FAMILY` twice in descriptors, while the later operator-instance CF tests use `"new_cf"`; duplicate default descriptors can obscure intended non-default CF coverage.
- `uint64add` requires little-endian eight-byte operands, so Java byte-order regressions would silently produce wrong sums.
- Native operator ownership is subtle because `Options`/`ColumnFamilyOptions` can outlive or replace Java merge operator wrappers.
- Empty merge operator names are allowed but `null` names must throw `IllegalArgumentException`.

### Test Signals

Signals are exact merged values (`aa,bb`, `aabb`, `aa<>bb`, `101`, `257`, `250`) and expected exceptions for null names. Static research only; no test command was run.
