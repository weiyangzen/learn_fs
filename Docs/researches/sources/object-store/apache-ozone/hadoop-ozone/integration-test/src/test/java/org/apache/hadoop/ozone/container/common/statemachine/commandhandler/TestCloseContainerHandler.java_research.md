# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerHandler.java

Purpose: This compact integration test verifies that a single datanode receiving a `CloseContainerCommand` closes an open container created by a client write. It focuses on the basic command-handler path without the broader multi-pipeline cases in `TestCloseContainerByPipeline`.

Important APIs and types: The file uses `MiniOzoneCluster`, `OzoneConfiguration`, `OzoneClientFactory`, `ObjectStore`, `OzoneOutputStream`, `OmKeyArgs`, `OmKeyLocationInfo`, `ContainerID`, `ContainerInfo`, `Pipeline`, `CloseContainerCommand`, `SCMCommand`, `NodeManager.addDatanodeCommand`, and `ContainerData.isOpen`.

Control flow: `setup` builds a one-datanode MiniOzoneCluster, sets a 1 GB container size, disables safemode pipeline creation, removes minimum RATIS volume free-space pressure, and waits for a factor-one pipeline. The test writes a small key, looks up its block location through OM, resolves the SCM container and pipeline, asserts the datanode container is not closed, queues a `CloseContainerCommand` with the SCM leader term, waits until `isContainerClosed` returns true, and asserts the final state.

State and persistence behavior: The test observes local datanode container state in `ContainerSet`. A successful command transitions the key-value container out of open state, which also implies local container metadata has been updated by the handler. The test does not inspect SCM lifecycle state or persisted DB contents.

Dependencies and integration points: Coverage is the command path from SCM node manager queue to datanode command dispatcher and close handler, with OM and SCM lookup used only to find the target container and pipeline. Configuration touches safemode and volume free-space thresholds so the single-node cluster can create the needed pipeline.

Risks: The OM lookup uses `StandaloneReplicationConfig.getInstance(ONE)` for a key created with RATIS factor one, which relies on compatible lookup behavior in this test path. The helper method treats any non-open state as closed, so it would also pass for quasi-closed states.

Test signals: The main signal is a transition from `ContainerData.isOpen() == true` to false within five seconds after the command is queued to the datanode ID.
