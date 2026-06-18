# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/Table.java

## Purpose

`Table` defines the evolving metadata key-value table contract used by Ozone DB stores. It abstracts typed keys and values, basic CRUD, iteration, cache hooks, range scans, and SST import/export. The complete 395-line source was read for this report.

## Important APIs, Types, and Functions

Core methods are `put`, `putWithBatch`, `isEmpty`, `isExist`, `get`, `getSkipCache`, `getReadCopy`, `getIfExist`, `delete`, `deleteWithBatch`, `deleteRange`, `iterator`, `keyIterator`, `valueIterator`, `getName`, `getEstimatedKeyCount`, cache methods, `getRangeKVs`, `deleteBatchWithPrefix`, `dumpToFileWithPrefix`, and `loadFromFile`. Nested types are immutable `KeyValue<K,V>` and `KeyValueIterator<KEY,VALUE>`.

## Control Flow

Default iterator helpers wrap the main key-value iterator and project keys or values through `TableIterator.convert`. Many cache-related default methods throw `NotImplementedException`, making cache support explicit in implementations such as `TypedTable`.

## State and Persistence Behavior

The interface does not own state. Implementations persist mutations to a metadata backend, commonly RocksDB. Cache methods describe in-memory state that may contain recently committed or pending entries depending on implementation.

## Dependencies and Integration Points

It uses `BatchOperation`, `CodecException`, `RocksDatabaseException`, `MetadataKeyFilters.KeyPrefixFilter`, `TableCacheMetrics`, and cache key/value wrappers. `RDBTable` and `TypedTable` are direct implementers in this subset.

## Risks and Edge Cases

Default methods that throw can surprise callers when used against minimal implementations. `getReadCopy` intentionally has implementation-specific reference semantics. `getRangeKVs` documentation states snapshot-like listing, but concrete implementations must provide that behavior. `TableIterator.convert.seek` applies the converter to a possibly null seek result, which depends on caller/implementation behavior.

## Test Signals

Contract tests should cover CRUD, batch writes/deletes, range listing semantics, iterator projections, cache hook support/unsupported behavior, and equality/hash behavior for `KeyValue`.
