# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TableIterator.java

## Purpose

`TableIterator` is the closeable iterator contract for metadata table scans, adding RocksDB-style seek/remove operations to Java `Iterator`. The complete 105-line source was read for this report.

## Important APIs, Types, and Functions

The interface extends `Iterator<T>` and `Closeable`, with `close`, `seekToFirst`, `seekToLast`, `seek(KEY)`, and `removeFromDB`. Static `convert` adapts a `Table.KeyValueIterator` into another iterator shape.

## Control Flow

Concrete iterators implement navigation and removal. `convert` delegates all operations to the wrapped iterator and maps `next()`/`seek()` results through a provided function.

## State and Persistence Behavior

The interface owns no state. Implementations may hold native RocksDB iterators and remove persistent entries via `removeFromDB`.

## Dependencies and Integration Points

It depends on `Table.KeyValueIterator`, `RocksDatabaseException`, and `CodecException`. It is used by `Table.keyIterator`, `Table.valueIterator`, `RDBTable`, and `TypedTable`.

## Risks and Edge Cases

`close()` throws `RocksDatabaseException`, so callers should use compatible try-with-resources handling. `removeFromDB` mutates storage and should be used carefully while iterating. `convert.seek` does not guard null before applying the converter.

## Test Signals

Tests should cover adapter delegation, close propagation, seek conversion, remove propagation, and behavior when wrapped seek returns null.
