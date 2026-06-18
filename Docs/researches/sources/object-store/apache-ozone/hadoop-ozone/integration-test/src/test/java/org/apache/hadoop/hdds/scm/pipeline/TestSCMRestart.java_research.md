<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMRestart.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMRestart.java

Purpose: Tests SCM restart and recovery of persisted pipeline objects and reuse of recovered pipelines for new allocations.

Important APIs and types: Uses `MiniOzoneCluster`, `StorageContainerManager`, `ContainerManager`, `PipelineManager`, `Pipeline`, `ContainerInfo`, `RatisReplicationConfig`, and replication factors one and three.

Control flow: `BeforeAll` starts four datanodes, allocates a Ratis three container for owner `Owner1` and a Ratis one container for owner `Owner2`, opens both pipelines, restarts SCM with persistence, and refreshes managers. The test fetches both pipelines by ID after restart, compares object identity and equality with pre-restart pipeline objects, then allocates another Ratis three container for `Owner1`.

State and persistence behavior: Pipeline metadata and container-to-pipeline ownership survive SCM restart. After restart, objects are new Java instances but equal in persisted identity/content. Matching-container allocation should choose the same recovered pipeline for the same owner.

Dependencies and integration points: Covers SCM metadata store reload, pipeline manager equality semantics, container manager matching allocation, and restart of storage container manager while datanodes continue.

Risks: Static cluster and pipeline fields mean initialization failures affect all tests. The test assumes owner/pipeline matching will continue to reuse the first pipeline under current container-per-owner policy.

Test signals: Signals are `assertNotSame` but `assertEquals` for both recovered pipeline objects, and new container allocation using the original Ratis three pipeline ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMRestart.java -->
