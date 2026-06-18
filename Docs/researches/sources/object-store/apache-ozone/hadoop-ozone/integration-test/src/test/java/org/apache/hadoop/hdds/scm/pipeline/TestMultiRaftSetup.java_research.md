<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestMultiRaftSetup.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestMultiRaftSetup.java

Purpose: Verifies multi-Raft pipeline creation behavior with and without disallowing repeated peer sets.

Important APIs and types: Uses `MiniOzoneCluster`, `NodeManager`, `PipelineManager`, `ReplicationConfig`, `PipelineID`, `Pipeline`, `DatanodeDetails`, and config keys `OZONE_DATANODE_PIPELINE_LIMIT`, `OZONE_SCM_DATANODE_DISALLOW_SAME_PEERS`, and `OZONE_SCM_PIPELINE_DESTROY_TIMEOUT`.

Control flow: Tests start clusters with three or five datanodes and pipeline limit two. With same peers allowed, two Ratis three pipelines are expected on three datanodes and each datanode's peer list contains the other nodes. With same peers disallowed, only one Ratis three pipeline can form on three datanodes and only two on five datanodes; explicit extra creation is expected to fail.

State and persistence behavior: Pipeline membership and node-to-pipeline counts live in SCM runtime state during each cluster. No restart persistence is tested.

Dependencies and integration points: Covers node peer-list tracking, pipeline placement constraints, automatic pipeline creation, and explicit pipeline creation failure when no valid peer set remains.

Risks: `assertNotSamePeers` removes from the list returned by `nodeManager.getAllNodes`, so it assumes a mutable copy. Shutdown is manual inside each test rather than an `@AfterEach`, increasing cleanup sensitivity if assertions fail before shutdown.

Test signals: Signals include exact Ratis three pipeline counts, `IOException` on impossible pipeline creation, one datanode with three total pipelines in the five-node case, and pipeline breakdown of one factor-one plus two factor-three pipelines for that datanode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestMultiRaftSetup.java -->
