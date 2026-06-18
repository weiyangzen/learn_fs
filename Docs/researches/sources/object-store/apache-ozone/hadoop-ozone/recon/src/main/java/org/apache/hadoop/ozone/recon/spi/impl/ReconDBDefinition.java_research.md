# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/ReconDBDefinition.java

Purpose: Defines the internal Recon RocksDB layout by extending `DBDefinition.WithMap`. The definition is the single registry of column families used by the Recon RocksDB store.

Important APIs/types: static `DBColumnFamilyDefinition` constants for `CONTAINER_KEY`, `KEY_CONTAINER`, `CONTAINER_KEY_COUNT`, `REPLICA_HISTORY`, `NAMESPACE_SUMMARY`, `REPLICA_HISTORY_V2`, `FILE_COUNT_BY_SIZE`, and `GLOBAL_STATS`. The constructor accepts the DB name, `getName` returns that runtime name, and `getLocationConfigKey` points to `OZONE_RECON_DB_DIR`.

State and persistence: the class defines persisted key/value codecs: `ContainerKeyPrefixCodec`, `KeyPrefixContainerCodec`, `LongCodec`, `NSSummaryCodec`, `ContainerReplicaHistoryList` codec, `FileSizeCountKey` codec, and `GlobalStatsValue` codec. The unmodifiable column-family map is what `DBStoreBuilder.createDBStore` uses to open or create Recon's store.

Dependencies and integration: consumed by `ReconDBProvider.initializeDBStore`; manager implementations retrieve typed tables through these definitions. The old `REPLICA_HISTORY` and newer `REPLICA_HISTORY_V2` coexist, which preserves upgrade compatibility while allowing bcsId-aware history.

Risks: adding or renaming a column family here is a storage-format change. Code that writes SQL global stats and RocksDB `GLOBAL_STATS` can create two stats stores with different lifecycles. Codec compatibility for protobuf-backed keys is critical because existing RocksDB data is read through these definitions at startup.

Test signals: codec tests and DB-provider tests are the main signals. Add coverage when introducing new families to verify DB open, staged DB open, and round-trip encoding for each persisted key/value pair.
