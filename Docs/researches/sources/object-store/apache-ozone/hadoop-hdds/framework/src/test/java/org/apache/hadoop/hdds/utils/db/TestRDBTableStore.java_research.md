# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBTableStore.java

Purpose: Broad integration coverage for raw `RDBTable` operations and typed table access over RocksDB column families.

Important APIs/types/functions: `RDBTable`, `Table.put/get/delete/deleteRange`, `putWithBatch`, `deleteWithBatch`, `iterator`, `getRangeKVs`, `dumpToFileWithPrefix`, `loadFromFile`, `isExist`, `getIfExist`, `getEstimatedKeyCount`, `RDBMetrics`, and typed table creation with `StringCodec`, `ByteStringCodec`, and `CacheType`.

Control flow: Setup creates normal and fixed-prefix column families. Tests cover handle retrieval, put/get/empty state, deletes and range deletes, batch writes/deletes, cross-codec typed reads, iterator counts, `isExist` and `getIfExist` metrics, large-value `ByteBuffer` reads, estimated row counts, iterator removal at several positions, prefixed byte/string iteration, prefixed range fetches, and dump/load of prefix-specific SST data including empty dumps.

State and persistence behavior: Mutates real RocksDB tables, closes/reopens store in existence tests, inspects metrics counters, writes dump files, and tests prefix extractor behavior.

Dependencies and integration points: Uses managed RocksDB options, RocksDB prefix extractors, Ozone metadata filters, protobuf `ByteString`, random test data, and `TypedTable`.

Risks: Static `count` is not reset per test and may cross-contaminate if tests are reordered. Random strings and prefix ordering can complicate reproductions. Metrics assertions couple tests to exact implementation counters.

Test signals: Excellent API-surface signal for raw table CRUD, batching, iterators, prefix scans, range reads, metrics, dump/load, and typed-codec interoperability.
