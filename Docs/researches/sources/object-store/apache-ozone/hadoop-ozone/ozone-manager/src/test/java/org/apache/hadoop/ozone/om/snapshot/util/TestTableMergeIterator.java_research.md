# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/util/TestTableMergeIterator.java

## Purpose
`TestTableMergeIterator` validates `TableMergeIterator`, a utility that iterates a caller-provided key stream and returns the values for each key across multiple tables in fixed table order.

## Important APIs, Types, and Functions
- `TableMergeIterator<K,V>` is constructed from `Iterator<K> keysToFilter`, an optional prefix, and one or more `Table<K,V>` instances.
- `next()` returns `Table.KeyValue<K, List<V>>` where the list index corresponds to the input table index and missing values are `null`.
- `StringInMemoryTestTable` supplies simple in-memory table behavior.
- `close()` is expected to be safe and idempotent enough for test usage.

## Control Flow
Tests cover constructor creation, `hasNext` delegation, single-key lookup in all tables, partial table hits, no hits, multiple sequential keys, empty tables, `NoSuchElementException` after exhaustion, prefix usage, single-table operation, null keys, large 100-key iteration, and sparse requested keys. A dedicated test asserts that the returned values list is mutable and reused across `next()` calls.

## State and Persistence Behavior
State is in-memory only. The iterator maintains the current key and a reusable values list, which is an explicit behavior: callers must not retain the list expecting immutability or snapshot isolation across iterations.

## Dependencies and Integration Points
The utility depends on the HDDS `Table` abstraction and `KeyValue` return type. It is relevant to snapshot table-merge workflows where a candidate key list must be compared across active and snapshot tables.

## Risks and Edge Cases
The test covers null keys and absent values but does not simulate table I/O exceptions during `get`, concurrent table mutation, or prefix mismatch filtering beyond a matching prefix case. The reusable list behavior is a notable integration risk for callers that cache results.

## Test Signals
The file establishes deterministic merge ordering and missing-value semantics, both essential for callers that compare per-key state across multiple metadata tables.
