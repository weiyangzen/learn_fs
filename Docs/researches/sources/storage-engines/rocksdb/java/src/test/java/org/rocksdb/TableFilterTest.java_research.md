# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/TableFilterTest.java

## Purpose

This suite verifies that a Java `AbstractTableFilter` installed in `ReadOptions` is invoked while iterating over table files and receives table properties for each column family.

## Important APIs and types

The test uses `DBOptions`, `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `ReadOptions.setTableFilter`, `AbstractTableFilter`, `TableProperties`, `FlushOptions`, and `RocksIterator`.

## Control flow

The test opens default and custom column families, writes three keys to each, flushes both, then iterates each CF using the same read options containing a collecting table filter. The nested filter stores `TableProperties.getColumnFamilyName()` values and always returns true.

## State and persistence behavior

Flush persists SST files so iteration must consult table files and trigger filter callbacks. The callback state is a Java list of CF names.

## Dependencies and integration points

This validates Java callback lifetime through `ReadOptions`, table properties conversion, and callback invocation from the native read path.

## Risks and test signals

Risks include callback not being pinned, missing CF name in properties, wrong callback order, or filter omission for one CF. Signals are exactly two collected names matching default and `new_cf`.
