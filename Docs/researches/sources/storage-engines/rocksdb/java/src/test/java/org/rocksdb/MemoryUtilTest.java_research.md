# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MemoryUtilTest.java

## Purpose

Integration coverage for `MemoryUtil.getApproximateMemoryUsageByType` over DBs and caches.

## Important APIs, control flow, and dependencies

The tests open one or two DBs using `BlockBasedTableConfig` with `LRUCache`, write/flush/get a key to create memtable, table reader, and cache usage, then call `MemoryUtil.getApproximateMemoryUsageByType`. Results are compared to DB aggregate properties `rocksdb.size-all-mem-tables`, `rocksdb.cur-size-all-mem-tables`, and `rocksdb.estimate-table-readers-mem`. A null-input test expects absent map values.

## State, persistence, risks, and test signals

State spans memtables, flushed SST table readers, block cache contents, and multiple DB handles. Risks include approximate counter instability, property-name drift, cache stats changes, and aggregation mistakes across DBs/caches. Signals are equality with DB properties for memtable/table-reader counts, cache usage increasing after reads, and null results for null input sets.
