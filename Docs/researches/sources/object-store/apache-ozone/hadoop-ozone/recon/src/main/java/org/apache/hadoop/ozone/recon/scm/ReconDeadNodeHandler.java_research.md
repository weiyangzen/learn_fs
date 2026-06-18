## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconDeadNodeHandler.java

Purpose: `ReconDeadNodeHandler` extends SCM's dead-node processing with Recon-specific reconciliation against SCM and immediate refresh of health/pipeline background tasks.

Important APIs and types: constructor accepts `NodeManager`, `PipelineManager`, `ContainerManager`, `StorageContainerServiceProvider`, a container-health `ReconScmTask`, and `PipelineSyncTask`. `onMessage(DatanodeDetails, EventPublisher)` is the main hook.

Control flow: the handler first delegates to `DeadNodeHandler` for normal SCM node/pipeline/container cleanup. It then pulls all SCM nodes through `scmClient.getNodes`, matches by UUID, updates Recon node operational state if SCM has a record, and triggers `containerHealthTask.initializeAndRunTask()` plus `pipelineSyncTask.initializeAndRunTask()`.

State and persistence: state changes happen through `ReconNodeManager.updateNodeOperationalStateFromScm`, which updates in-memory node status and datanode details; pipeline and container-health tasks persist through their own managers and SQL/DB tables.

Dependencies and integration points: registered for `SCMEvents.DEAD_NODE` by the facade. It depends on the SCM service provider for authoritative node operational state and on background tasks to recompute derived health data after the node transition.

Risks and edge cases: `getNodes()` fetches the full SCM node list and scans it on each dead-node event, which may be costly in large clusters. If SCM lacks the node, Recon logs a warning and proceeds with task triggers. Exceptions skip both task refreshes because all post-super work is in one try block.

Test signals: no direct test was found. Good coverage would mock SCM node states, assert operational-state correction, and verify health/pipeline tasks are triggered after dead events and not before parent processing.
