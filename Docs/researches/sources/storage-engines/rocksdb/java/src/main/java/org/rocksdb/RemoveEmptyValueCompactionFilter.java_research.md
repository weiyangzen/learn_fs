# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RemoveEmptyValueCompactionFilter.java

## Purpose
`RemoveEmptyValueCompactionFilter` is a Java wrapper around RocksDB's native `RemoveEmptyValueCompactionFilter`. It lets Java options install a compaction filter that drops entries with empty values during compaction.

## Important APIs, Types, And Functions
- Constructor calls native `createNewRemoveEmptyValueCompactionFilter0()` and passes the handle to `AbstractCompactionFilter<Slice>`.
- Native creation in `remove_emptyvalue_compactionfilterjni.cc` allocates `ROCKSDB_NAMESPACE::RemoveEmptyValueCompactionFilter`.

## Control Flow
Java construction is a direct JNI allocation. Filtering decisions happen entirely in C++ during compaction; this Java class does not override Java callback methods.

## State And Persistence Behavior
The Java object owns a native compaction filter pointer through the `AbstractCompactionFilter`/native-reference hierarchy. The filter has no Java-visible mutable state. Its effects are persistent because compaction rewrites SST data and omits empty-value entries.

## Dependencies And Integration Points
- Extends `AbstractCompactionFilter<Slice>`.
- Uses C++ utility header `utilities/compaction_filters/remove_emptyvalue_compactionfilter.h`.
- Can be installed on `Options` or `ColumnFamilyOptions` via compaction-filter APIs.
- Test helper `RemoveEmptyValueCompactionFilterFactory` returns new instances for factory-based configuration.

## Risks And Edge Cases
- Because filtering happens during compaction, existing empty-value entries may remain until relevant files compact.
- Installing the filter can delete legitimate empty values if the application uses empty byte arrays as meaningful values.
- Lifecycle matters: options must retain the filter for as long as native RocksDB may call it.

## Test Signals
- `OptionsTest` and `ColumnFamilyOptionsTest` exercise setting the direct filter and factory variant.
- Strong behavioral tests should insert empty and non-empty values, force compaction, and verify only empty values are removed.
