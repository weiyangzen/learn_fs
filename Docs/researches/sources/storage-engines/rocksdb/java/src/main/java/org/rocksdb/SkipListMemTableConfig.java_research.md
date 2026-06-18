# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SkipListMemTableConfig.java

## Purpose
`SkipListMemTableConfig` configures RocksDB's skip-list memtable representation, specifically the seek lookahead optimization.

## Important APIs and Types
- Extends `MemTableConfig`.
- Constant `DEFAULT_LOOKAHEAD = 0`.
- Constructor initializes `lookahead_`.
- Fluent setter `setLookahead(long)`.
- Getter `lookahead()`.
- Overrides `newMemTableFactoryHandle()` to call native `newMemTableFactoryHandle0(long)`.

## Control Flow
Users configure the object by calling `setLookahead`, then options code calls `newMemTableFactoryHandle()` to allocate the native memtable factory with the configured value. Native code may throw `IllegalArgumentException` for invalid lookahead values.

## State and Persistence Behavior
The only Java state is `lookahead_`. It affects future native memtable factory creation and therefore runtime write-path/read-seek behavior inside RocksDB, but it does not itself persist data. Once applied to DB options, the native factory participates in in-memory write buffering.

## Dependencies and Integration Points
It depends on `MemTableConfig` and JNI. It integrates with column-family/options configuration that accepts memtable factories.

## Risks
No Java-side validation is performed on `lookahead`; invalid values are deferred to native code. Because the setter is mutable and unsynchronized, callers should finish configuration before sharing it. The optimization is workload-specific and can hurt if configured blindly.

## Test Signals
Tests should verify default value, fluent setter return identity, getter accuracy, native factory creation for valid values, and native rejection for invalid values.
