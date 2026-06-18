# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestSchemaTwoBackwardsCompatibility.java

Purpose: This suite verifies that containers created under schema-v2 remain readable and deletable after schema-v3 is enabled. It models the upgrade assumption that schema-v2 containers are closed before upgrade and must continue to use their original DB layout.

Important APIs and types: It uses `ContainerTestUtils.disableSchemaV3` and `enableSchemaV3`, `KeyValueContainerData` with `SCHEMA_V2`, `BlockManagerImpl`, `FilePerBlockStrategy`, `DatanodeStoreSchemaTwoImpl`, `DeletedBlocksTransaction`, `BlockDeletingServiceTestImpl`, `BlockIterator`, `KeyValueHandler`, and mocked `OzoneContainer`/`ContainerDispatcher`.

Control flow: Setup disables schema-v3, initializes a volume set, block manager, file-per-block chunk manager, container set, handler, and ozone-container mock. `createTestContainer` creates a schema-v2 container, writes six blocks with two chunks each, and inserts two delete transactions of two blocks each while updating metadata. Tests then enable schema-v3 before reading or deleting. They verify DB file placement, block iteration and chunk lengths, metadata reads, and deletion via transaction processing.

State and persistence behavior: The suite persists schema-v2 DB state below the container path, not the shared schema-v3 DB. It writes real chunk files and block records, stores delete transactions in the schema-v2 transaction table keyed by long transaction ID, and updates metadata keys for latest delete transaction and pending delete count. After deletion, it checks in-memory and DB metadata for block count, pending-delete count, and bytes used.

Dependencies and integration points: It exercises upgrade-aware `BlockUtils.getDB`, schema detection, transaction table decoding, block manager writes, chunk manager filesystem writes, metadata table reads, and deletion service execution after the global config switches to schema-v3.

Risks: The test relies on file-per-block layout and fixed constants, so it does not cover file-per-chunk schema-v2 upgrade behavior here. The helper uses `startBlockID = txnID * DELETE_TXNS_PER_CONTAINER`, which matches current constants but would need review if transaction sizing changes.

Test signals: Schema remains `SCHEMA_V2`, DB file parent path is the container ID, iterator returns six blocks with two 1024-byte chunks, metadata values match six blocks and four pending deletes, and deletion leaves two live blocks, zero pending deletes, and expected bytes used.
