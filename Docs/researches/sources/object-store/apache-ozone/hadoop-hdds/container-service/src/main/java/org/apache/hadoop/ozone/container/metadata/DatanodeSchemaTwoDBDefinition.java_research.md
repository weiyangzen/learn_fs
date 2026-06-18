## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaTwoDBDefinition.java

Purpose: Defines schema-two datanode container DB layout with separate physical column families for block data, metadata, delete transactions, finalized blocks, and last-chunk information.

Important APIs and functions: Static column family definitions include `BLOCK_DATA`, `METADATA`, `DELETE_TRANSACTION`, `FINALIZE_BLOCKS`, and `LAST_CHUNK_INFO`. `getMap()` exposes the DBDefinition map. Accessors return each schema component, with delete transactions keyed by `Long`.

Control flow and state: The definition is immutable and per container DB path. Unlike schema three, schema two does not prefix every key with container ID because each DB belongs to one container.

Persistence and dependencies: Uses `StringCodec` for block/metadata keys, `LongCodec` for transaction IDs and values, `FixedLengthStringCodec` for finalized blocks and last-chunk records, `Proto2Codec` for `DeletedBlocksTransaction`, and `BlockData` codecs.

Risks: Delete transaction keys are only transaction IDs, so schema-two stores must not be shared across containers. Mixing fixed-length and normal string codecs by table means callers must route keys to the correct table. Last-chunk table availability is required for incremental chunk list support.

Test signals: Open schema-two DBs, put/get/delete transactions by long ID, finalized block iteration, last-chunk incremental writes, block data CRUD, and migration behavior from schema one where relevant.
