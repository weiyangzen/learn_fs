# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCloseContainerByPipeline.java

Purpose: This class tests datanode close-container command handling for containers associated with SCM pipelines. It validates handler invocation, standalone one-node closure, RATIS three-node closure, DB separation across pipeline members, and the quasi-closed to closed transition path.

Important APIs and types: It uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneOutputStream`, `OmKeyArgs`, `OmKeyLocationInfo`, `ContainerInfo`, `Pipeline`, `CloseContainerCommand`, `SCMCommand`, `CommandHandler`, `NodeManager.addDatanodeCommand`, `KeyValueContainerData`, `BlockUtils.getDB`, `DBHandle`, and datanode `ContainerData` state predicates.

Control flow: The class starts one shared ten-datanode cluster with low owner-container count and expanded pipeline limits, creates a volume and bucket, then each test writes a key to create an open container. `testIfCloseContainerCommandHandlerIsInvoked` finds the target datanode and close handler, queues a `CloseContainerCommand`, waits for the container to close, and asserts invocation count increased. The standalone test closes a one-replica RATIS container and verifies later pipeline closure does not reopen or alter closed state. The RATIS test sends close commands to each of three pipeline datanodes, captures each local container DB handle, asserts distinct DB stores, and waits for every replica to close. The quasi-close test closes the pipeline first, waits for quasi-closed state, then sends a forced close command.

State and persistence behavior: The observable state is local datanode `ContainerData` transitioning from open to closed or quasi-closed, plus container metadata DB handles for each RATIS replica. SCM state is used to locate pipelines and provide the leader term on queued commands, but assertions focus on datanode container state.

Dependencies and integration points: It covers SCM command queuing, datanode command dispatcher, close container handler, Ratis group/pipeline closure behavior, OM key location lookup, and key-value container metadata DB access.

Risks: The class uses a shared static cluster, so failed tests can leave state for later methods. The quasi-close test is marked unhealthy. Some comments mention standalone even though current writes use RATIS with factor one, reflecting historical terminology.

Test signals: Signals include close-handler invocation count growth, closed state on target datanodes, closed state persisting after pipeline close, distinct RocksDB metadata stores for RATIS replicas, and forced close moving a quasi-closed container to closed.
