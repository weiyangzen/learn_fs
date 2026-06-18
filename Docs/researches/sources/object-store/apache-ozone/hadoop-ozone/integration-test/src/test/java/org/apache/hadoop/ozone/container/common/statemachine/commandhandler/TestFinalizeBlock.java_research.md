# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestFinalizeBlock.java

Purpose: This parameterized integration test verifies finalize-block semantics for both legacy and schema V3 key-value container layouts. It ensures that a finalized block rejects later write chunk and put block requests, reloads finalized-block state after datanode restart, and clears finalized-block state after container close.

Important APIs and types: The test uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneOutputStream`, `OmKeyArgs`, `OmKeyLocationInfoGroup`, `ContainerInfo`, `Pipeline`, `XceiverClientManager`, `XceiverClientSpi`, `ContainerTestHelper.getWriteChunkRequest`, `getPutBlockRequest`, `getFinalizeBlockRequest`, `BlockID`, `KeyValueContainerData.getFinalizedBlockSet`, and `DatanodeConfiguration.CONTAINER_SCHEMA_V3_ENABLED`.

Control flow: `setup` creates a one-datanode cluster for the selected schema mode with short report intervals and block deletion intervals. The test writes a key, locates the first container and local block ID, acquires an xceiver client for the pipeline, verifies write chunk and put block work before finalization, sends a finalize-block request, and asserts the response local ID matches the key block. It then checks that the finalized block set contains one entry, verifies later write chunk and put block fail with "Block already finalized", restarts the datanode and checks the finalized set reloads, closes all containers, waits for the finalized set to clear, restarts again, and checks it remains empty.

State and persistence behavior: The core state is `KeyValueContainerData.finalizedBlockSet`. The test verifies it is persisted or reconstructed across datanode restart while the container is open, then removed when the container closes and remains absent across a second restart. It also validates that finalized block state gates write-path commands, not read-path behavior.

Dependencies and integration points: Coverage spans raw container protocol commands over the xceiver client, OM key metadata lookup, key-value container metadata, schema-version configuration, datanode restart/reload behavior, and SCM-driven container close.

Risks: The test uses the first SCM container and the first key location, which is valid for the single-node, single-key setup but would be fragile if setup changed. It asserts exception message text for rejected writes. `XceiverClientManager` is not explicitly closed in the test body.

Test signals: Strong signals are successful pre-finalize write/put, finalize response local ID equality, finalized set size one, rejected write chunk and put block after finalization, finalized set size one after restart, empty finalized set after close, and empty finalized set after the second restart for both schema modes.
