## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStore.java

Purpose: Defines the typed table and block access contract for datanode container metadata stores.

Important APIs and functions: Accessors expose block data, metadata, deleted blocks, finalize blocks, and last-chunk tables. Iterators expose block and finalize-block traversal with optional filters. `getBlockByID()` fetches block data by key and delegates to `getCompleteBlockData()`. `putBlockByID()` has a default old-client behavior that overwrites the block data table.

Control flow and state: This interface extends `DBStoreManager`. Default methods encode common block lookup/update behavior while allowing incremental chunk-list stores to override completion and put logic.

Persistence and dependencies: Tables are RocksDB-backed through HDDS `Table`. It integrates `BlockID`, `BlockData`, `ChunkInfoList`, `BatchOperation`, `KeyValueContainerData`, and `KeyPrefixFilter`.

Risks: `getDeletedBlocksTable()` exists for schema one compatibility but is unsupported in base schema-two/three implementations. Default `getCompleteBlockData()` throws `NO_SUCH_BLOCK` for null data; incremental stores may recover data from last-chunk table. Batch callers must commit through the store's batch handler.

Test signals: Table access for each schema, default block missing exception, incremental override behavior, batch put by local ID, filtered block iteration, finalize-block iteration, and deleted-block table support only for schema one.
