## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaThreeDBDefinition.java

Purpose: Defines schema-three datanode DB layout with separate column families and fixed-length container-ID prefixes for shared per-volume RocksDB databases.

Important APIs and functions: Column families cover `block_data`, `metadata`, `delete_txns`, `finalize_blocks`, and `last_chunk_info`, all with fixed-length string keys. `getContainerKeyPrefix()`, `getContainerKeyPrefixBytes()`, `getContainerKeyPrefixLength()`, `getKeyWithoutPrefix()`, and `getContainerId()` encode/decode prefixes. The constructor sets the separator and configures each CF with a fixed-length prefix extractor.

Control flow and state: `separator` is static and set from datanode configuration in the constructor. CF options are read per column family from optional RocksDB config or from the datanode DB profile, then modified for prefix seek.

Persistence and dependencies: Uses `FixedLengthStringCodec`, `LongCodec`, `Proto2Codec` for delete transactions, `BlockData` codecs, HDDS DB definitions, and RocksDB managed CF options. `DatanodeStoreSchemaThreeImpl` relies on these prefixes for per-container iteration, dump/load, delete, and compaction.

Risks: Static separator changes affect all schema-three definitions in the JVM. Prefix length must match fixed-length encoded container IDs plus separator exactly or prefix seek and compaction ranges break. `getKeyWithoutPrefix()` uses the first separator occurrence, so separator choice must not conflict with encoded prefixes.

Test signals: Validate key prefix round trips, container ID extraction from smallest/largest SST keys, prefix bytes length, per-CF prefix extractor setup, custom options-file handling, delete transaction key encoding, and iteration constrained to one container.
