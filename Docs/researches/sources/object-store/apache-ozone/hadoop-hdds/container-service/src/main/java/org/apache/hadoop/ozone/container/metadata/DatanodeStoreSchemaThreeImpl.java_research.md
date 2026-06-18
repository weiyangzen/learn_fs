## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaThreeImpl.java

Purpose: Implements schema-three container metadata storage over shared, container-prefixed RocksDB tables, including delete transaction access, per-container export/import, removal, iteration, and small-SST compaction.

Important APIs and functions: `getDeleteTransactionTable()` exposes string-keyed delete transactions. `getBlockIterator()` and `getFinalizeBlockIterator()` constrain iterators by container prefix. `removeKVContainerData()` deletes all prefixed rows for a container in one batch. `dumpKVContainerData()` and `loadKVContainerData()` export/import SST files per table. `compactionIfNeeded()` scans live SST metadata and compacts ranges with too many small files.

Control flow and state: The store inherits incremental chunk-list behavior. Dump/load process metadata, block data, optional last-chunk data gated by layout feature finalization, and delete transactions. Compaction groups live files by column family and level, computes min/max container IDs for small files, then compacts a prefix range.

Persistence and dependencies: Persists to schema-three column families using fixed-length prefixed keys. Depends on RocksDB live file metadata, SST file readers, compact range options, `VersionedDatanodeFeatures`, `HDDSLayoutFeature.HBASE_SUPPORT`, and `DatanodeSchemaThreeDBDefinition` prefix helpers.

Risks: Prefix delete/dump/load affects all rows with a container prefix; prefix encoding bugs can remove another container's data. Loading SST dumps decodes every key/value and batches puts, so malformed dump files fail import. Compaction range `endCId + 1` must avoid overflow. Missing empty dump files are treated as no-op.

Test signals: Per-container iteration isolation, delete transaction CRUD, remove all prefixed data, dump/load round trip including empty files, HBASE_SUPPORT on/off last-chunk handling, small-SST compaction thresholds, unknown CF warning, and import failure on corrupt SST data.
