# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/util/ParallelTableIteratorOperation.java

Purpose: `ParallelTableIteratorOperation` parallelizes RocksDB table scanning by deriving key-range bounds from SST metadata, running bounded iterator tasks, and handing batches to worker tasks.

Important APIs and types: the constructor accepts metadata manager, table, key codec, iterator and worker counts, max values in memory, and log threshold. `performTaskOnTableVals(taskName, startKey, endKey, Function<KeyValue<K,V>,Void>)` executes the scan. `close()` shuts down iterator and worker executors.

Control flow: `getBounds` attempts to read RocksDB live SST file metadata from `RDBStore`, filters by column family name, decodes smallest and largest keys, adds optional start/end keys, sorts, and filters. If fewer than two bounds exist, the operation falls back to a single table iterator with optional seek/end stop. Otherwise, it submits one iterator task per adjacent bound pair. Iterator tasks collect key-value batches up to `maxNumberOfVals`, throttle pending worker futures, and submit worker tasks that apply the caller function and update progress counters. The method waits for all iterator and worker futures before returning.

State and persistence: no durable writes. State is executor queues, future queues, decoded bounds, and counters. The caller's function may persist results.

Dependencies: HDDS `Table`, `TableIterator`, `Codec`, `RDBStore`, OM metadata manager, RocksDB `LiveFileMetaData`, Java executors.

Risks and test signals: executor queues are unbounded even though future throttling limits submitted backlog. Bound handling can double-process boundary keys if SST ranges overlap or duplicated bounds are present. `waitForQueueSize` propagates worker failures through future `get`. Tests should cover fallback path, start/end ranges, SST-bound segmentation, duplicate bounds, interruption, worker exception propagation, and executor shutdown.
