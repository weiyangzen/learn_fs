# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestHelper.java

Purpose: `TestHelper` is a shared utility class for Ozone container integration tests. It centralizes key creation, data validation, container and pipeline close waits, datanode container lookup, replica counting, SCM state waits, and replication input definitions used by RATIS and EC tests.

Important APIs and types: The helper wraps `ObjectStore`, `OzoneOutputStream`, `OzoneDataStreamOutput`, `KeyOutputStream`, `KeyDataStreamOutput`, `BlockOutputStreamEntry`, `BlockDataStreamOutputEntry`, `MiniOzoneCluster`, `MiniOzoneHAClusterImpl`, `StorageContainerManager`, `ContainerManager`, `ContainerInfo`, `ContainerReplica`, `Pipeline`, `XceiverServerRatis`, `StateMachine`, and `GenericTestUtils.waitFor`. The nested `ReplicationInput` enum maps RATIS to three datanodes and `RatisReplicationConfig.getInstance(THREE)`, and EC to five datanodes and `new ECReplicationConfig(3, 2)`.

Control flow: Container presence and closed checks scan cluster datanode services for a matching `DatanodeDetails` and inspect `ContainerSet`. Key helpers create RATIS or EC keys and stream keys through Ozone client APIs. `waitForContainerClose` overloads extract container IDs from output-stream entries, locate pipelines through SCM, wait for containers to appear and be open on all pipeline nodes, fire `SCMEvents.CLOSE_CONTAINER`, then wait until each datanode reports closed container data. Pipeline-close helpers ask SCM's pipeline manager to close pipelines, then poll each datanode's Ratis server until the Raft group is gone. Replica-count waits poll SCM container replica records.

State and persistence behavior: The helper reads live datanode `ContainerSet` state, SCM container metadata, pipeline manager state, and Ratis server group state. `validateData` performs durable data verification by reading a key and comparing file hashes. The helper does not persist state itself, but it drives state transitions through SCM event queue and pipeline manager APIs.

Dependencies and integration points: It is a cross-cutting fixture for client I/O, OM key block streams, SCM container/pipeline managers, datanode state machines, Ratis write channels, HA SCM leader selection, and Ozone metrics/logging through assertions.

Risks: Helpers assume key output streams are `KeyOutputStream` or `KeyDataStreamOutput` implementations and write channels are `XceiverServerRatis` for pipeline close validation. Some waits have fixed timeouts that can be tight on slow environments. Direct firing of close events bypasses higher-level operational flows by design.

Test signals: Reusable signals include boolean container presence/closed status, exact replica count in SCM, matching read/write hashes, pipeline Raft group disappearance, SCM lifecycle state equality, and non-empty extracted container ID lists from client streams.
