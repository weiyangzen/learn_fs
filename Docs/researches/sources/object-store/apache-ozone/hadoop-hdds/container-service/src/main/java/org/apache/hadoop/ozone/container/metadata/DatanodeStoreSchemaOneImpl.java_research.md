## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaOneImpl.java

Purpose: Opens and exposes a schema-one datanode store, preserving logical deleted-block table access over the legacy default column family.

Important APIs and functions: The constructor builds an `AbstractDatanodeStore` with `DatanodeSchemaOneDBDefinition`, then obtains and checks the deleted-block logical table. `getDeletedBlocksTable()` returns a `SchemaOneDeletedBlocksTable` wrapper that adds/removes the schema-one deleted prefix.

Control flow and state: The store inherits block and metadata table setup from the abstract base and maintains a `deletedBlocksTable` field for schema-one-specific access.

Persistence and dependencies: All logical data is persisted in RocksDB's default CF with schema-one codecs. It depends on `DatanodeTable`, `SchemaOneDeletedBlocksTable`, and `ChunkInfoList`.

Risks: Each `getDeletedBlocksTable()` call creates a new wrapper; this is cheap but means object identity is not stable. Prefix handling must be centralized in the wrapper so callers do not double-prefix. Value decoding may return null for old deleted-block records without chunk info.

Test signals: Construct schema-one stores, use deleted-block put/get/delete/range without caller prefixes, verify physical `#deleted#` storage, access normal block/metadata tables, and close/read-only open behavior.
